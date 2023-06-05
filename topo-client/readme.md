# Install Python Packages
`pip3 install -r requirements.txt`

# Install `Yarrp`
## Dependencies

### CentOS, Fedora
```
sudo yum -y install autoconf
sudo yum -y install automake
sudo yum -y install zlib-devel
```
### Other
```
sudo apt-get -y install autoconf
sudo apt-get -y install automake
sudo apt-get -y install libz-dev 
```

## Install
```
git clone https://github.com/cmand/yarrp.git
./bootstrap
./configure
make
```


# Configure
Modify `config.cfg`

* `YARRP_DIR=<Directory of Your Yarrp>`

(Absolute path of the executable yarrp, e.g., use `/root/yarrp/yarrp` instead of `/root/yarrp`)

* `INTERFACE_NAME=<Your Network Interface>`

(For example, `eth0`. You can check with `ifconfig`)

* `LOCAL_IPV4_ADDRESS=<Your Local IPv4 Address>`

* `LOCAL_IPV6_ADDRESS=<Your Local IPv6 Address>`

(Make sure that it's consistent with the interface you filled above)

# Usage
`python3 topo-client.py`