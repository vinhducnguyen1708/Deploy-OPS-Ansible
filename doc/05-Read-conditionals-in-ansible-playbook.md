# Conditionals in ansible playbook
- Trong quá trình chạy các tasks việc đặt điều kiện là rất cần thiết, vừa có tác dụng làm cho các tasks được chạy theo đúng kịch bản được yêu cầu, vừa dùng làm để check trước khi chạy các task khác.

## Cách sử dụng conditionals trong playbook
- Ansible cung cấp cho ta 1 statement `when` được định nghĩa ở cuối các tasks, cùng bậc với module.

- Statement `when` đọc và chấp nhận các định dạng của jinja2

- Ví dụ:
    ```yaml
    tasks:
    - name: "shut down Debian flavored systems"
        command: /sbin/shutdown -t now
        when: ansible_facts['os_family'] == "Debian"
    ```
    
    - Task trên sẽ thực hiện shutdown host client với điều kiện ( `when` )  các host đó có os thuộc distro `Debian`

## Sử dụng conditionals trong playbook deploy OPS
**1. Điều kiện cho việc tạo dựng Cluster**
- Sử dụng để phân biệt chạy cluster hoặc không.
    - Sử dụng template cấu hình nếu chỉ chạy 1 node controller: Filter độ dài các hosts trong group có giá trị nhỏ hơn 2 thì sẽ chạy task này.
    ```yaml
    - name: Config Mariadb if only have one node Controller
      template:
        src: openstack.cnf.j2
        dest: /etc/my.cnf.d/openstack.cnf
      when:
       - groups['controller'] | length  < 2
    ```

    - Sử dụng template cấu hình cho cụm cluster nếu có 3 node controller:
    ```yaml
    - name: Config Mariadb Cluster
      template:
        src: cluster.cnf.j2
        dest: /etc/my.cnf.d/cluster.cnf
      when:
        - groups['controller'] | length  == 3
    ```

- Sử dụng để phân biệt node nào sẽ khởi tạo cluster
    - Mặc định host đầu tiên được định nghĩa trong group `[controller]` sẽ là node khởi tại cluster.
    - `[0]` là thứ tự đầu tiên trong group `[controller]`
    
    - Nếu `inventory_hostname` là controller1.hn.vnpt thì `inventory_hostname_short` sẽ được dịch là controller1
    ```yaml
    - name: Create Galera Cluster
      shell: /usr/bin/galera_new_cluster
      when:
        - inventory_hostname_short ==  hostvars[groups['controller'][0]]['inventory_hostname_short']
    ```

**2. Điều kiện cho việc cấu hình các service OPS**
- Khi Cài đặt các service OPS trên cụm 3 controller, ta cũng chỉ phải tạo Database, Domain, user, endpoint cho các service ở 1 node hoặc việc copy fernet key của keystone sang các node còn lại cũng vậy. Nên việc sử dụng statement `when` là cần thiết.

- Vì độ phức tạp không như khi làm việc với cluster nên có 2 cách sử dụng.
  - Cách 1: Sử dụng statement `when` như việc phân biệt node khởi tạo cluster như ở trên

  - Cách 2: Sử dụng statement `run_once`, sẽ chỉ chạy 1 lần ở node bất kỳ (thường là node đầu tiên trong group). Ví dụ dưới sẽ sử dụng module `mysql_db` để tạo db cho các service, module `os_keystone_endpoint` là module ansible cung cấp tương tác với openstack client. 
  ```yaml
  ### Trong file ../roles/install_glance/tasks/bootstrap.yml
  ---
  - name: Create database for Glance
    mysql_db:
      login_user: root
      login_password: "{{ mariadb_pass }}"
      login_port: 3306
      login_host: "{{ IP_VIP }}"
      name: glance
      state: present
    run_once: true
    ...

  ### Trong file ../roles/install_glance/tasks/register.yml
  ...
  - name: Create endpoint
  os_keystone_endpoint:
     auth: "{{ openstack_auth }}"
     service: glance
     endpoint_interface: "{{ item }}"
     url: http://{{ IP_VIP }}:9292
     region: "{{ REGION }}"
     state: present
  with_items:
    - public
    - admin
    - internal
  run_once: true
  ...
  ```

**3. Điều kiện cho việc chạy các tasks kèm với check các file đã tồn tại**
- Ví dụ. Đối với các file backup cấu hình thì nếu chỉ chạy 1 task đơn giản như dưới đây rồi sau khi chạy lại sẽ lại tiếp tục backup file cấu hình đó dẫn đến mất file cấu hình gốc của OPS:
```yaml
- name: Backup file config glance-api.conf
  copy:
    src: /etc/glance/glance-api.conf
    dest: /etc/glance/glance-api.conf.bak
    remote_src: yes
```

- Vậy nên ta sẽ sử dụng điều kiện đối với phần này
  - Đầu tiên thực hiện check status của file chỉ định:
    - module `stat` dùng để check status 1 file hoặc dir
    - `register` có nhiệm vụ lưu lại kết quả của task vừa chạy thành 1 biến.
  ```yaml
  - name: Check /etc/glance/glance-api.conf.bak existed
    stat:
      path: /etc/glance/glance-api.conf.bak
    register: glance_api_conf_bak
  ```
  - Thực hiện back up file cấu hình cùng với điều kiện when
    - Sử dụng module `copy` để copy file, cùng option `remote_src: yes` là để copy các file từ host, nếu không set ansible sẽ tìm file này trên node deployment.
    - `when: - not glance_api_conf_bak.stat.exists` : glance_api_conf_bak là biến được lưu bằng `register` ở trên, `.stat.exists` là các thông tin về biến trả về cho `glance_api_conf_bak`. Task này sẽ chạy với điều kiện không tồn tại file  `/etc/glance/glance-api.conf.bak` nếu tồn tại rồi thì SKIP

  ```yaml
  - name: Backup file config glance-api.conf
    copy:
      src: /etc/glance/glance-api.conf
      dest: /etc/glance/glance-api.conf.bak
      remote_src: yes
    when: 
      - not glance_api_conf_bak.stat.exists
  ```

