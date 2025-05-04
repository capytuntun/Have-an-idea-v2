
>[!info] 
>可能可以找到帳密等檔案，並且可能可以使用匿名登入
### 登入FTP
```shell
 ftp 192.168.2.142 
```
### 暴力破解FTP
```shell
medusa -u fiona -P /usr/share/wordlists/rockyou.txt -h 10.129.203.7 -M ftp 
```