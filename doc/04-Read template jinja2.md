# Variables in file jinja2 

## Một số biến được dùng trong playbook
**1. Các biến được định nghĩa**
```yaml
...
metadata_secret: 5b721855305f81836b04
mariadb_pass: 6c4c795a4b866e4f82f4
rabbitmq_pass: ed4150476a71d98c6a55

### network interface
IP_VIP: 192.168.10.150
IP_VIP_NETMASK: 24
REGION: Hanoi
MGNT_IF: eth0
DATA_IF: eth1
FLAT_IF: eth2
...
```
- Đây là các biến do ta tự định nghĩa nên. Các biến này được gọi vào các tasks hay các templates bằng cách: `{{ REGION }}`
- Ví dụ cách gọi biến:
```yaml
## ví dụ trong file ../roles/install_nova/templates/nova.conf
...
[database]
connection = mysql+pymysql://nova:{{ novadb_pass }}@{{ IP_VIP }}/nova
...
[glance]
api_servers = http://{{ IP_VIP }}:9292
...
```
**2. Các biến lấy từ việc garther_facts của ansible**
```yaml
### IP setup var
MGNT_IP: "{{ hostvars[inventory_hostname]['ansible_' + MGNT_IF]['ipv4']['address'] }}"
#### MGNT NETWORK setup var
MGNT_NETWORK: "{{  hostvars[inventory_hostname]['ansible_' + MGNT_IF]['ipv4']['network'] }}" 
```
- Giải thích: 
    ```yaml
    MGNT_NETWORK: "{{ hostvars[inventory_hostname]['ansible_' + MGNT_IF]['ipv4']['network'] }}"
    ```
    - `hostvars`: bản chất thì hostvars là một `magic variable` của ansible sẽ cho chúng ta access biến của host được chỉ định, bao gồm cả  việc thu thập các facts của host đó khi không chạy playbook trên host đó. 

    - Sau đó là các thông tin về biến đó được nối bằng [ ]
    
    - `[inventory_hostname]`: chỉ định host đang chạy playbook đó.

    - `['ansible_' + MGNT_IF]`: bản chất là `['ansible_eth0']` nhưng do muốn native phần card mạng nên ta set như trên. thì đây là biến ám chỉ thông tin về tên card mạng (sẽ lấy thông tin trên interface nào)

    - `['ipv4']`: lấy thông tin ip dạng ipv4
    - `['network']`: Lấy địa chỉ network 
    
    - Kết quả trả về cho biến trên đó là: Sử dụng module `debug` thực hiện test biến trả về
    ```yaml
    PLAY [controller] *************************************************************

    TASK [Gathering Facts] *************************************************************
    ok: [controller1.hn.vnpt]

    TASK [test yum] *************************************************************
    ok: [controller1.hn.vnpt] => {
        "MGNT_NETWORK": "192.168.10.0"
    }

    PLAY RECAP *************************************************************
    controller1.hn.vnpt        : ok=2    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0

    ```

- Ví dụ cách gọi biến templates:
    - Nếu chúng ta chỉ gọi biến ở trên thì kết quả trả về sẽ chỉ là IP address hoặc IP network của 1 host hoặc nếu khai báo lại từng biến với chỉ định host thay vì [inventory_hostname] mà bằng [host1], [host2],... như thế sẽ rất dài và giá trị sử dụng lại không cao. Vậy cần sử dụng một vài các kỹ thuật về vòng lặp trong file jinja2
    
    - Ví dụ:
    ```yaml
    ## ví dụ trong file ../roles/install_nova/templates/nova.conf
    ...
    transport_url = rabbit://{%- for item in groups['controller'] %}openstack:{{ rabbitmq_pass }}@{{  hostvars[item]['ansible_' + MGNT_IF]['ipv4']['address'] }}:5672{% if not loop.last %},{% endif %}{% endfor %}
    ...
    memcached_servers = {%- for item in groups['controller'] %}{{  hostvars[item]['ansible_' + MGNT_IF]['ipv4']['address'] }}:11211{% if not loop.last %},{% endif %}{% endfor %}
    ```
    - Giải thích: option `transport_url`
        - `rabbit://`: là phần không bị thay đổi, cố định đầu dòng
        
        - `{%- for item in groups['controller'] %}`: khai báo vòng lặp. Với `item` tất cả các host trong group `controller` được định nghĩa ở file inventory. `{%-` có dấu trừ tức là các biến xuất ra sẽ nằm trên cùng 1 dòng ( nếu không có thì sẽ xuống dòng ).

        - `openstack:{{ rabbitmq_pass }}@{{  hostvars[item]['ansible_' + MGNT_IF]['ipv4']['address'] }}:5672`: sẽ thực hiện vòng lặp với các biến có giá trị host `item` là các host trong group `controller`.

        - `{% if not loop.last %},`: Khai báo điều kiện trong vòng lặp. Sau các biến được cách nhau bởi dấu phẩy ở cuối, nếu kết thúc vòng lặp mà không còn biến nào được sinh ra thì sẽ không còn dấu phẩy, có thể thay dấu phẩy bằng nhiều kí tự khác hay cả dấu cách.

        - `{% endif %}`: kết thúc điều kiện
        
        - `{% endfor %}`: kết thúc vòng lặp

    - Kết quả trả về cho biến trên:
    ```ini
    transport_url = rabbit://openstack:rabbitpass@192.168.10.101:5672,openstack:rabbitpass@192.168.10.102:5672,openstack:rabbitpass@192.168.10.103:5672
    ```