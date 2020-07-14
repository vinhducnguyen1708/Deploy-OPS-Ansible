# Tài liệu hướng dẫn triển khai Openstack bằng Ansible

## Ý nghĩa các biến trong Playbook

1. Các biến ít thay đổi trong `group_vars/all.yml`

*Những biến dưới đây là những biến ít thay đổi hoặc các biến được thu thập từ việc chạy gather_facts của ansible*

```yml
### Database config
- Khai báo thông tin tên của user replicate khi khi sử dụng multisite
replicate_user: repl

### Openstack config Auth enviroment
- Khai báo về môi trường khởi tạo cho Openstack
#### Admin
openstack_auth:
  auth_url: "{{ keystone_protocol }}://{%- if enable_multisite | bool %}{{ IP_VIPSITE1 }}{% else %}{{ IP_VIP }}{% endif %}:{{ keystone_port }}/v3"
  username: "admin"
  password: "{{ admin_pass }}"
  project_name: "admin"
  domain_name: "Default"
  user_domain_name: "Default"
#### Octavia
- Khai báo môi trường khi khởi tạo resource để sử dụng octavia service.
openstack_octavia_auth:
  auth_url: "{{ keystone_protocol }}://{%- if enable_multisite | bool %}{{ IP_VIPSITE1 }}{% else %}{{ IP_VIP }}{% endif %}:{{ keystone_port }}/v3"
  username: "octavia"
  password: "{{ octavia_pass }}"
  project_name: "service"
  domain_name: "Default"
  user_domain_name: "Default"


### SSL config
- Khai báo các thông tin khi cấu hình sử dụng HTTPS
- cafile_name là tên file cert
cafile_name: haproxy
- openstack_cacert là đường dẫn đến file cert
openstack_cacert: "{% if enable_ssl | bool %}/etc/ssl/private/{{ cafile_name }}.pem{% else %}{% endif %}"

#### Docker Config
- Khai báo thông tin khi cài đặt docker. role  install_docker chỉ chạy khi chạy multisite
- Khi cài đặt docker nếu sử dụng proxy thì khai báo các thông tin dưới đây.
enable_docker_proxy: "no"
IP_docker_proxy: 172.16.68.49
Port_docker_proxy: 3128

#### Openstack services
- Khai báo các thông tin cài đặt các services cho Openstack
- Các biến này sẽ được lấy ra để đưa vào trường điều kiện (when) khi chạy role ( nếu có giá trị bool thì role sẽ được chạy )
enable_openstack_core: "yes"
enable_keystone: "{{ enable_openstack_core | bool }}"
enable_glance: "{{ enable_openstack_core | bool }}"
enable_placement: "{{ enable_openstack_core | bool }}"
enable_nova: "{{ enable_openstack_core | bool }}"
enable_neutron: "{{ enable_openstack_core | bool }}"
enable_horizon: "{{ enable_openstack_core | bool }}"

### Version Packages
mariadb_version: 10.4

### Openstack services config
keystone_port: 5000

### Create VMs
- Dưới đây là các khai báo thông tin để tạo VMs và các resources khác
#### Selfservice network info:
- Khai báo các thông số tạo selfservice network
selfservice_network_name: service_network
sub_selfservice_network_name: sub1_selfservice_network
selfservice_network_address: 192.168.178.0/24
selfservice_dns_nameservers: 8.8.8.8
selfservice_pool_start: 192.168.178.10
selfservice_pool_end: 192.168.178.200

#### Provider network info:
- Khai báo tạo flat network, dây cũng là khai báo thông tin về flat network cho octavia nên lưu ý!
provider_network_name: provider_network
sub_provider_network_name: sub1_provider_network
provider_network_address: 192.168.30.0/24
provider_network_type: flat
provider_physical_network: physnet1
provider_dns_nameservers: 8.8.8.8
provider_pool_start: 192.168.30.230
provider_pool_end: 192.168.30.245

#### Router info:
- Khai báo tên Router
router_name: Routeradmin

#### Flavor info:
- Khai báo thông tin flavor
flavor_name: tiny
flavor_ram: 1024
flavor_vcpus: 1
flavor_root_disk: 5


### Do not touch :(
#### SSL
#public_protocol: "{{ 'https' if enable_tls | bool else 'http' }}"
#internal_protocol: "{{ 'https' if enable_tls | bool else 'http' }}"
- keystone_protocol sẽ trả về 2 giá trị http hoặc https khi giá trị của enable_ssl là bool. 
keystone_protocol: "{{ 'https' if enable_ssl | bool else 'http' }}"
- keystone_url là địa chỉ xác thực của keystone 
keystone_url: "{{ keystone_protocol }}://{{ IP_VIP }}:{{ keystone_port }}/v3"


#### Token
- Khai báo các tính toán về gia hạn Fernet-key
token_expired_min: "{{ token_expiration_keystone * 60 | int }}"
token_expired_sec: "{{ token_expiration_keystone * 3600 | int }}"
number_keystone_node: "{{ groups['controller'] | length | int }}"
rotation_frequency: "{{ token_expired_sec | int  // number_keystone_node | int  }}"
max_active_keys: "{{ token_expired_sec | int  // rotation_frequency | int + 2  }}"
### IP setup var
- Các biến này sẽ trả về các giá trị network của các node trong quá trình gather_facts do Ansible thực hiện
##### ex: MGNT_IP's output will be "192.168.10.101"
MGNT_IP: "{{ hostvars[inventory_hostname]['ansible_' + MGNT_IF]['ipv4']['address'] }}"
DATA_IP: "{{ hostvars[inventory_hostname]['ansible_' + DATA_IF]['ipv4']['address'] }}"
FLAT_IP: "{{ hostvars[inventory_hostname]['ansible_' + FLAT_IF]['ipv4']['address'] }}"
#### MGNT NETWORK setup var
##### ex: MGNT_NETWORK's output will be "192.168.10.0"
MGNT_NETWORK: "{{  hostvars[inventory_hostname]['ansible_' + MGNT_IF]['ipv4']['network'] }}"
##### ex: MGNT_IPADD's output will be "192.168.10.0/255.255.255.0"
MGNT_IPADD: "{{ MGNT_NETWORK }}/{{ MGNT_NETMASK }}"
##### ex: MGNT_CIDR's output will be "192.168.10.0/24"
MGNT_CIDR: "{{ MGNT_IPADD | ipaddr('net') }}"
MGNT_NETMASK: "{{  hostvars[inventory_hostname]['ansible_' + MGNT_IF]['ipv4']['netmask'] }}" 
#### FLAT NETWORK setup var
##### ex: FLAT_NETMASK's output will be "255.255.255.0"
FLAT_NETMASK: "{{  hostvars[inventory_hostname]['ansible_' + FLAT_IF]['ipv4']['netmask'] }}"
```


2. Các biến dùng để Customise hệ thống Openstack

`customise.yml`

*Đây là file khai báo các thông số để customise hệ thống Openstack. Việc khai báo file này là bắt buộc trước khi chạy Ansible để deploy hệ thống Openstack. Và file biến này được gọi vào bằng option `-e` ví dụ : `-e@custimse.yml`*
```yml
Việc đầu tiên cần làm khi dựng hệ thống Openstack là làm việc với các interfaces. Ở mục này sẽ khai các thông tin về network cho hệ thống Openstack.

## Network interface
### IP VIP info
- Khai báo thông tin IP_VIP là IP để đi ra ngoài Internet khi triển khai mô hình HA.( Phải là IP chưa bị sử dụng )
- Khi triển khai 1 node controller thì khai báo IP_VIP là IP của node controller đó.
IP_VIP: 192.168.10.50
IP_VIP_NETMASK: 24

### Interfaces info
- Khai báo các interface sẽ được sử dụng cho từng chức năng
MGNT_IF: eth0
DATA_IF: eth1
FLAT_IF: eth2

## All file stored in:
- Ở đây sẽ khai báo đường dẫn đến THƯ MỤC. Thư mục này sẽ được tạo ra để lưu trữ các file được sinh ra trong quá trình triển khai hệ thống.
ansible_deploy_files: /root/AnsibleOPSfiles

## Openstack info
- Khai báo tên Region cho cụm Openstack
REGION: Hanoi

### Rotate key info
- Ở đây sẽ khai báo thông tin về fernet key cho cụm Openstack
- token_expiration_keystone là thời hạn token tồn tại ( tính theo giờ )
- fernet_rotate_log_file file lưu log rotate key
- fernet_rotate_crontab_file là file crontab để thực hện rotate key
token_expiration_keystone: 2
fernet_rotate_log_file: /var/log/keystone/keystone-fernet-rotate.log
fernet_rotate_crontab_file: /var/spool/cron/keystone

### Openstack multi-site config
- Đây là mục khai báo thông tin về dựng Openstack multisite. Khi khai báo enable_multisite: "yes" thì Sẽ triển khai cụm Openstack được kết nốt với cụm đã triển khai
enable_multisite: "no"

#### Infomation SITE1
- Khai báo thông tin về tên Region và IP của cụm cần liên kết
REGION1: Hanoi
IPCON1_SITE1: 192.168.10.51
IPCON2_SITE1: 192.168.10.52
IPCON3_SITE1: 192.168.10.53
IP_VIPSITE1: 192.168.10.50

### Services version
mariadb_version: 10.2

### Services 
#### HA services
- Khi triển khai mô hình HA thì 2 tham số enable cho haproxy và pacemaker chuyển thành "yes" thì sẽ thực hiện chạy role cài đặt Haproxy và Pacemaker( install_haproxy và install_pacemaker )
- Khi triển khai mô hình đơn node thì bắt buộc set 2 biến này thành "no"
enable_haproxy: "yes"
enable_pacemaker: "yes"

#### Openstack's services
- Tại đây khai báo các service Openstack sẽ được cài đặt. Khi các tham số enable của các service được set là "yes" thì sẽ thực hiện chạy các role cài đặt tương ứng.
- enable_openstack_core là các service core của hệ thống Openstack (keysonte, glance, placement, nova, neutron, horizon)
enable_openstack_core: "yes"
enable_cinder: "yes"
enable_barbican: "yes"
enable_heat: "yes"
enable_octavia: "yes"

## Storage Backend
#### LVM backend
- Khai báo các thông tin khi sử dụng storage backend LVM thì set "yes"
- Những khai báo này được dựa trên node cinder-volume
cinder_volume_group: cinder-volumes
enable_lvm: "no"
lvm_disk: vdb

### CEPH backend
- Khai báo khi sử dụng storage backend là ceph thì set "yes"
enable_ceph: "yes"
- Khai báo IP của 1 node trong cụm ceph cluster
CEPH_MGR_IP: 192.168.10.40

## SSL
Khai báo sử dụng protocol HTTPS để giao tiếp giữa các services thì set "yes"
enable_ssl: "yes"  
```


