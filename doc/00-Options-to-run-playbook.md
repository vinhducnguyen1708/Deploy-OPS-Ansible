# Options to run my playbook

## Action 

- Ở đây ta định nghĩa 1 biến là `my_action`, biến này không nằm ở bất cứ file variable nào vì biến này ta truyền vào khi thực hiện lệnh để chạy playbook bằng option `-e` ( extra var ) của lệnh ansible.

- Để **DEPLOY** hệ thống Openstack sử dụng lệnh
```sh
### my_action=deploy
ansible-playbook -i multinodeHA  Deploy_OPS_main.yml -e my_action=deploy
```
- Để **RESTART SERVICES OPS**( restart tất cả ) khi đã deploy xong:
```sh
### my_action=restart_service
ansible-playbook -i multinodeHA  Deploy_OPS_main.yml -e my_action=restart_service
```
- Để **RECONFIGURE OPS SERVICES** ( reconfig lại tất cả services ) khi đã deploy xong:
```sh
### my_action=reconfigure
ansible-playbook -i multinodeHA  Deploy_OPS_main.yml -e my_action=reconfigure
```
*Hiện tại việc khai báo biến `my_action` là bắt buộc khi cài các service OPS và chỉ có tác dụng reconfigure, restart service đối với các roles service OPS, còn các service cài môi trường chưa bổ sung, nhưng thêm biến `my_action` cũng sẽ không ảnh hưởng đến việc cài đặt các service môi trường đó.*


## Run single role
- Ở đây chia thành các role chạy từng service để thực hiện cài hệ thống Openstack nên có chạy chỉ định từng role
```sh
### Chỉ cài đặt ntp
ansible-playbook -i multinodeHA Deploy_OPS_main.yml -t install_ntp -e my_action=deploy
### Chỉ cài đặt cấu hình các thành phần hostname, repo, disable service,..
ansible-playbook -i multinodeHA Deploy_OPS_main.yml -t baremental -e my_action=deploy
### Chỉ cài đặt keystone
ansible-playbook -i multinodeHA Deploy_OPS_main.yml -t install_keystone -e my_action=deploy
```
## Restart or Reconfigure single service

- Thay vì việc ssh vào trong từng node thì ansible sẽ giải quyết vấn đề này nhanh gọn nhẹ :)

```sh
### Chỉ restart service của keystone và nova
ansible-playbook -i multinodeHA  Deploy_OPS_main.yml -t install_keystone,install_nova -e my_action=restart_service
```





