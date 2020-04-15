# Inventory file
Inventory file là nơi khai báo các host để node deployment có thể remote. Bắt buộc phải khai báo IP hoặc hostname của các node client để node deployment có thể sử dụng ssh để giao tiếp

## Nội dung file Inventory
**Nội dung**
```
[controller]
controller1.hn.vnpt ansible_ssh_host=192.168.10.101
controller2.hn.vnpt ansible_ssh_host=192.168.10.102
controller3.hn.vnpt ansible_ssh_host=192.168.10.103

[compute]
compute1.hn.vnpt ansible_ssh_host=192.168.10.181
```
- Để deploy hệ thống Openstack nên tạm thời khai báo 2 group là `[controller]` và `[compute]` nếu hệ thống phức tạp hơn và có nhiều thành phần thì nên khai báo thêm các group như `[mariadb]`,`[heat]`,..

- Ở cột đầu tiên trong các group đó là `inventory_hostname` đây sẽ được ansible coi là special variable và có thể sử dụng trong các task bằng cách `{{ inventory_hostname }}` thì biến này sẽ có giá trị inventory_hostname của node đang chạy playbook đó ( chạy trên node 192.168.10.101 thì {{ inventory_hostname }} có giá trị là controller1.hn.vnpt )

- cột thứ 2 sẽ khai báo địa chỉ node cần ssh đến.

- Vậy việc cần làm khi khai báo với file inventory này là:
    - Khai báo node ấy muốn tên là gì như cột thứ nhất
    - địa chỉ để ansible có thể giao tiếp với node client

