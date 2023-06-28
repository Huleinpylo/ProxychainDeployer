import os

def generate_tf_file():
    #v region = input("Enter the AWS region for EC2 instances: ")
    instance_count = input("Enter the number of EC2 instances to create: ")
    instance_type = input("Enter the EC2 instance type: ")

    tf_content = f'''
    provider "aws" {{
      access_key = "-----------------------"
      secret_access_key = "--------------------------"
      region = "us-east-1"
    }}

    resource "aws_instance" "debian_instance" {{
      count = {instance_count}

      ami = "ami-0a9d5908c7201e91d" // https://wiki.debian.org/Cloud/AmazonEC2Image/Bullseye
      instance_type = "{instance_type}"

      key_name = "mykey"

      provisioner "local-exec" {{
        command = "ansible-playbook -i '${{self.public_ip}},' -u admin  --private-key=mykey playbook.yml"
      }}

      lifecycle {{
        ignore_changes = [key_name]
      }}

      tags = {{
        Name = "Debian Instance ${{count.index + 1}}"
      }}
    }}
    '''

    with open("main.tf", "w") as tf_file:
        tf_file.write(tf_content)

    print("The Terraform file has been generated successfully.")

def generate_ssh_key():
    key_name = input("Enter the SSH key name: ")
    os.system(f"ssh-keygen -t rsa -b 4096 -f {key_name}")

    print("The SSH key pair has been generated successfully.")

def generate_proxychain_conf(ip_addresses):
    with open("proxychain.conf", "w") as conf_file:
        conf_file.write("strict_chain\n")
        conf_file.write("proxy_dns\n")
        conf_file.write("[ProxyList]\n")
        for ip in ip_addresses:
            conf_file.write(f"socks5 {ip} 9666\n")

    print("The proxychain.conf file has been generated successfully.")

def launch_resources():
    os.system("terraform init")
    os.system("terraform apply")

    # Get the IP addresses of the instances
    output = os.popen("terraform output -json").read()
    ip_addresses = output.strip().split('\n')[1:]

    print("The AWS resources have been launched successfully.")
    print("IP addresses:")
    for i, ip in enumerate(ip_addresses, start=1):
        print(f"Instance {i}: {ip}")

    generate_proxychain_conf(ip_addresses)

def destroy_resources():
    os.system("terraform destroy")

    print("The AWS resources have been destroyed successfully.")

def main():
    while True:
        print("--- Menu ---")
        print("1. Generate Terraform file")
        print("2. Generate SSH key pair")
        print("3. Launch AWS resources")
        print("4. Destroy AWS resources")
        print("5. Quit")

        choice = input("Choose an option: ")

        if choice == "1":
            generate_tf_file()
        elif choice == "2":
            generate_ssh_key()
        elif choice == "3":
            launch_resources()
        elif choice == "4":
            destroy_resources()
        elif choice == "5":
            break
        else:
            print("Invalid choice. Please try again.")

        input("Press Enter to continue...")

if __name__ == "__main__":
    main()
