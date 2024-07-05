import random
import string


def generate_invitation_codes(n, length=16):
    codes = set()
    chars = string.ascii_letters + string.digits  # 包括大小写字母和数字

    while len(codes) < n:
        code = ''.join(random.choice(chars) for _ in range(length))
        codes.add(code)

    return list(codes)


# 生成100个不重复的16位邀请码
invitation_codes = generate_invitation_codes(100)

sql_statements = [
    "DROP TABLE IF EXISTS `Invitation_code`;",
    """
    CREATE TABLE `Invitation_code` (
        `Invitation_code_id` INT AUTO_INCREMENT PRIMARY KEY,
        `code` VARCHAR(16) NOT NULL,
        `is_available` BOOLEAN NOT NULL,
        `used_at` DATETIME
    );
    """
]

# 为每个邀请码添加INSERT语句
for code in invitation_codes:
    sql_statements.append(
        f"INSERT INTO `Invitation_code` (`code`, `is_available`, `used_at`) VALUES ('{code}', TRUE, NULL);")

# 第三步：保存SQL语句到TXT文件


with open('invitation_codes.sql', 'w', encoding="utf-8") as file:
    for statement in sql_statements:
        file.write(statement + "\n")
        print(statement)

print("SQL语句已保存到invitation_codes.sql文件中。")
