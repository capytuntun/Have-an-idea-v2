import os
import re
import sys
import subprocess

def rename_images(root_folder):
    for folder_path, _, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.startswith("Pasted image"):
                new_name = filename.replace(" ", "_")
                old_path = os.path.join(folder_path, filename)
                new_path = os.path.join(folder_path, new_name)
                if old_path != new_path:
                    os.rename(old_path, new_path)
                    print(f"✅ Renamed: {old_path} → {new_path}")

def update_markdown_links(root_folder):
    md_pattern = re.compile(r'!\[\[(Pasted image [\d]+\.png)\]\]')

    for folder_path, _, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.endswith(".md"):
                md_path = os.path.join(folder_path, filename)
                with open(md_path, "r", encoding="utf-8") as f:
                    content = f.read()

                matches = md_pattern.findall(content)
                if matches:
                    for match in matches:
                        new_filename = match.replace(" ", "_")
                        new_markdown = f"![Pasted image](images/{new_filename})"
                        old_markdown = f"![[{match}]]"
                        content = content.replace(old_markdown, new_markdown)

                    with open(md_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"✏️ Updated Markdown: {md_path}")

def git_commit_and_push(root_folder, commit_msg):
    try:
        subprocess.run(["git", "-C", root_folder, "add", "."], check=True)
        subprocess.run(["git", "-C", root_folder, "commit", "-m", commit_msg], check=True)
        subprocess.run(["git", "-C", root_folder, "push"], check=True)
        print("🚀 Git commit & push 成功！")
    except subprocess.CalledProcessError as e:
        print("❌ Git 操作失敗：", e)

def main():
    if len(sys.argv) < 3:
        print("❌ 使用方式: python main.py <資料夾路徑> <commit message>")
        sys.exit(1)

    root = sys.argv[1]
    commit_msg = sys.argv[2]

    if not os.path.isdir(root):
        print(f"❌ 找不到資料夾：{root}")
        sys.exit(1)

    rename_images(root)
    update_markdown_links(root)

    git_commit_and_push(root, commit_msg)

    print("\n🎉 所有圖片檔名與 Markdown 語法已更新並推送到 GitHub！")

if __name__ == "__main__":
    main()
