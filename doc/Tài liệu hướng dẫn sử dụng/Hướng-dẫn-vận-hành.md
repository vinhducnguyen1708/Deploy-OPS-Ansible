# Tài liệu hướng dẫn vận hành Openstack bằng Ansible

1. Quản lý cấu hình 
2. Khởi động lại các services OPS

## Quản lý cấu hình

- Các file cấu hình của các roles cài đặt cho từng services được lưu ở thư mục `/Deploy-OPS-Ansible/roles/install-*/templates/`

- Khi thay đổi nội dung file cấu hình trong thư mục `/Deploy-OPS-Ansible/roles/install-*/templates/` thì thực hiện truyền giá trị vào biến `my_action` là `reconfigure` :
```sh
ansible-playbook -i multinodeHA Deploy_OPS_main.yml -e@customise.yml -e@passwords.yml -e my_action=reconfigure
```

- Nếu chỉ muốn thay đổi cấu hình của một vài service thì gắn tag vào câu lệnh:

```sh
ansible-playbook -i multinodeHA Deploy_OPS_main.yml -t install_octavia,install_nova,install_barbican -e@customise.yml -e@passwords.yml -e my_action=reconfigure
```

## Khởi động lại các services

- File task thực thi khởi động lại các services của từng roles nằm tại `/Deploy-OPS-Ansible/roles/install-*/tasks/restart_service.yml`

- Để thực hiện khởi động lại các service chỉ định thì ta thực hiện truyền giá trị vào biến `my_action` là `restart_service` :

```sh
ansible-playbook -i multinodeHA Deploy_OPS_main.yml -t install_octavia,install_nova,install_barbican -e@customise.yml -e@passwords.yml -e my_action=restart_service
```