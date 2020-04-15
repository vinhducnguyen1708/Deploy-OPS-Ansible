# Main plabook

Khi chạy ansible cần chỉ định chạy 1 playbook chính, vậy nên việc cần làm là đưa tất cả các thành phần cần cài đặt vào trong 1 playbook để ansible có thể gọi tới các thành phần đó qua playbook đó.

## Nội dung main playbook

- Main playbook ở đây là file yaml **Deploy_OPS_main.yml**. Tạm thời tất cả thành phần cài đặt được gọi tới qua playbook này. Nhưng việc chia tách phần cài đặt cấu hình môi trường và phần triển khai Openstack cần được tách ra.

***Nội dung:***
```
---
- name: Garther_facts
  hosts: all
  gather_facts: true
  tasks:
    - name: Group hosts to determine when using --limit
      group_by:
        key: "all_using_limit_{{ (ansible_play_batch | length) != (groups['all'] | length) }}"
  tags: always

- name: Apply role baremental
  gather_facts: false
  become: true
  hosts: all
  roles:
    - { role: baremental,
        tags: baremental }
- name: Apply role chrony
  gather_facts: false
  become: true
  hosts: all
  roles:
    - { role: install_ntp,
        tags: install_ntp }

- name: Apply role Mariadb
  gather_facts: false
  become: true
  hosts: controller
  roles:
    - { role: install_mariadb,
        tags: install_mariadb }

....
- name: Apply role Keystone
  gather_facts: false
  become: true
  hosts: controller
  roles:
    - { role: install_keystone,
        tags: install_keystone }
...
```
- Cấu trúc được chia nhỏ thành nhiều tác vụ(task) khác nhau. Mỗi task được phân ra mở 1 gạch đầu dòng bắt đầu được khai báo tên (name)


- `name: Garther_facts`: mục đích task này có nhiệm vụ thu thập các thông tin của các host bị điều khiển như: địa chỉ IP, card mạng, hostname, os-version,...

    - Module `group_by`: là module dùng để đọc nội dung file inventory và lưu vào bộ nhớ tạm thời, cùng với sử dụng option `key:"all_using_limit_{{ (ansible_play_batch | length) != (groups['all'] | length) }}"` với mục đích thực thi với các host đang thực hiện chạy playbook đồng thời.
    
    - `tags: always`: gắn tag cho 1 task này với giá trị `always` để ép buộc luôn phải chạy task khi chạy playbook

- `name: Apply role ... `: Đây là các task có mục đích gọi đến các role được chỉ định.
    
    - Việc set `garther_facts: false` là để không muốn chạy vì ở task đầu tiên ta đã làm việc đó rồi. nếu không set sẽ mặc định chạy và việc đó sẽ rất mất thời gian
    
    - `become: true`: là module để chạy tất cả các task dưới quyền root
    - `hosts:` đây là nơi khai báo các hosts hoặc các group sẽ được chỉ định để chạy task trên đó ( sử dụng cho việc phân chia các task chạy trên controller và compute ). Khai báo ở đây dưới dạng các group trong file inventory.
    - `roles:`  gọi đến 1 role cụ thể được lưu trong thư mục `roles` cùng đó là gắn tag cho role đó để khi dùng lệnh và khai báo `-t`(tags) thì sẽ chỉ chạy 1 hoặc nhiều role được chỉ định

    
