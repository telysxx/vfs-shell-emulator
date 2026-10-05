# Эмулятор оболочки с виртуальной файловой системой

Практическая работа № 1 по дисциплине «Конфигурационное управление»,
вариант № 6.

## 1. Общее описание

Консольный (CLI) эмулятор оболочки UNIX-подобной ОС на Python 3.10+.
Работает как REPL: выводит приглашение, читает команду, выполняет её.
Все файлы и каталоги находятся в **виртуальной файловой системе (VFS)**,
которая загружается из JSON-файла и целиком хранится в оперативной памяти.
Реальная файловая система не изменяется, исходный JSON не перезаписывается:
изменения после `cp` и `rmdir` пропадают при перезапуске.

Внешние библиотеки не нужны, используется только стандартная библиотека.

### Что реализовано по вариантам этапов

| Этап | Содержание |
|------|------------|
| 1. REPL | приглашение с именем VFS, раскрытие `$VAR` и `${VAR}` из окружения реальной ОС, ошибки (неизвестная команда, неверные аргументы), `exit` |
| 2. Конфигурация | параметры `--vfs`, `--prompt`, `--script`, `--config`; JSON-конфиг; приоритет командной строки над файлом; стартовый скрипт с комментариями; отладочный вывод параметров |
| 3. VFS | загрузка VFS из JSON (содержимое файлов в Base64), работа только в памяти |
| 4. Основные команды | `ls`, `cd`, `du`, `cat`, `find` |
| 5. Дополнительные команды | `rmdir`, `cp` |

## 2. Описание функций и настроек

### Параметры командной строки

| Параметр | Описание |
|----------|----------|
| `--vfs PATH` | путь к JSON-файлу с описанием VFS |
| `--prompt TEXT` | приглашение к вводу (шаблон, см. ниже) |
| `--script PATH` | путь к стартовому скрипту |
| `--config PATH` | путь к JSON-файлу конфигурации |

При запуске эмулятор печатает все итоговые параметры в формате
`ключ = значение`.

### Конфигурационный файл (JSON)

```json
{
  "vfs_path": "vfs_examples/multiple_files.json",
  "prompt": "{vfs}:{cwd}$ ",
  "startup_script": "scripts/emu/stage4.txt"
}
```

Допустимы только ключи `vfs_path`, `prompt`, `startup_script`; неизвестный
ключ — ошибка (это защищает от опечаток).

**Приоритет значений:** параметры командной строки → конфигурационный файл →
значения по умолчанию. Пустая строка в командной строке (например,
`--script ""`) тоже считается заданным значением и отключает скрипт из файла.

### Приглашение к вводу

В шаблоне приглашения можно использовать подстановки:
`{vfs}` — имя VFS (имя JSON-файла без расширения), `{cwd}` — текущий каталог
внутри VFS. Значение по умолчанию: `{vfs}:{cwd}$ `, например
`multiple_files:/home$ `.

### Парсер команд

* Раскрываются переменные окружения реальной ОС: `$HOME`, `${HOME}`.
  Неопределённая переменная раскрывается в пустую строку, как в UNIX-shell.
* Поддерживаются кавычки: `cp "a b" c`.
* Всё после неэкранированного `#` — комментарий.
* Ошибки (неизвестная команда, неверное число аргументов, несуществующий путь,
  незакрытая кавычка) выводятся как `Error: ...`, эмулятор продолжает работу.

### Стартовый скрипт

Текстовый файл, одна команда в строке. Пустые строки и комментарии (`#`)
пропускаются. При выполнении на экране отображаются приглашение, команда и
её вывод — как при живом диалоге. Если в скрипте встретилась команда `exit`,
эмулятор завершается; иначе после скрипта открывается интерактивный REPL.

### Формат VFS (JSON)

Узел — объект с полем `type`: `dir` (поле `children` — список узлов) или
`file` (поле `content_base64` — содержимое в Base64). Корень — каталог.

```json
{
  "name": "/",
  "type": "dir",
  "children": [
    {"name": "readme.txt", "type": "file", "content_base64": "TWluaW1hbCBWRlMK"},
    {"name": "home", "type": "dir", "children": []}
  ]
}
```

Проверяются типы узлов, корректность Base64, дубликаты и недопустимые имена.
Примеры: `vfs_examples/minimal.json` (минимальная),
`vfs_examples/multiple_files.json` (несколько файлов),
`vfs_examples/deep_tree.json` (три и более уровня вложенности).

### Команды

| Команда | Описание |
|---------|----------|
| `ls [path]` | содержимое каталога (у каталогов в конце `/`) |
| `cd [path]` | сменить каталог; без аргумента — корень VFS; `.` и `..` поддерживаются |
| `du [path]` | размер в байтах: сначала подкаталоги, последней строкой — сам путь |
| `cat <file>` | вывести содержимое файла |
| `find [path] <name>` | найти записи с точным именем `name` начиная с `path` (по умолчанию `.`) |
| `rmdir <dir>` | удалить **пустой** каталог (нельзя корень и текущий каталог) |
| `cp <src> <dst>` | копировать файл или каталог целиком; если `dst` — существующий каталог, копия кладётся внутрь под прежним именем |
| `exit` | выйти из эмулятора |

Служебные команды для демонстрации: `pwd` (текущий каталог) и
`tree [path]` (дерево каталогов).

## 3. Сборка, запуск и тесты

Сборка не требуется. Нужен Python 3.10 или новее.

```bash
bash run.sh                 # Linux / macOS: интерактивный REPL
run.bat                  # Windows
make run                 # то же через Makefile
```

Тесты (модуль `unittest`, запускать из корня репозитория):

```bash
make test
# или
python3 -m unittest discover -s tests -t . -v
```

Демонстрационные скрипты реальной ОС (`scripts/os/`), по одному на этап:

```bash
bash scripts/os/stage1.sh   # REPL, переменные окружения, ошибки
bash scripts/os/stage2.sh   # все параметры CLI, JSON, приоритеты, ошибки
bash scripts/os/stage3.sh   # минимальная VFS, несколько файлов, 3+ уровня
bash scripts/os/stage4.sh   # ls, cd, du, cat, find
bash scripts/os/stage5.sh   # rmdir, cp
make demo                   # все этапы подряд
```

Стартовые скрипты эмулятора лежат в `scripts/emu/`.

## 4. Примеры использования

Запуск с параметрами командной строки:

```console
$ bash run.sh --vfs vfs_examples/multiple_files.json --prompt "student> "
=== VFS emulator parameters ===
config_path    = <none>
vfs_path       = vfs_examples/multiple_files.json
prompt         = 'student> '
startup_script = <none>
cwd (real OS)  = /home/user/vfs-emulator
===============================
Type 'exit' to quit.
student> ls
bin/  etc/  home/  empty/  docs/
student> cd /home/student
student> ls ..
student/  guest.txt
student> cat notes.txt
UNIX-like shell emulator
student> exit
```

Запуск с конфигурационным файлом и переопределением параметра:

```console
$ bash run.sh --config config.json --prompt "override> " --script scripts/emu/stage2.txt
```

Поиск, размеры и обработка ошибок:

```console
multiple_files:/$ find / target.txt
/docs/deep/level2/target.txt
multiple_files:/$ du /home
31	/home/student
42	/home
multiple_files:/$ cat /missing.txt
Error: No such file or directory: /missing.txt
multiple_files:/$ cd a b
Error: Usage: cd [path]
multiple_files:/$ unknown_command
Error: unknown command: unknown_command
```

Изменения только в памяти:

```console
multiple_files:/$ cp /home/guest.txt /etc/guest_copy.txt
multiple_files:/$ cat /etc/guest_copy.txt
Guest file
multiple_files:/$ cp /empty /empty_copy
multiple_files:/$ rmdir /empty_copy
multiple_files:/$ rmdir /home
Error: Directory not empty: /home
```

Переменные окружения реальной ОС:

```console
$ DEMO_DIR=/home bash run.sh --vfs vfs_examples/minimal.json
minimal:/$ ls $DEMO_DIR
student.txt
minimal:/$ cd ${DEMO_DIR}
minimal:/home$ pwd
/home
```

Полный вывод всех демонстраций можно получить командой `make demo`.

## Структура репозитория

```text
.
├── src/                 исходный код (main, config, line_parser, shell, commands, vfs)
├── tests/               модульные тесты
├── vfs_examples/        примеры VFS в формате JSON
├── scripts/emu/         стартовые скрипты эмулятора
├── scripts/os/          демонстрационные скрипты ОС (bash)
├── config.json          пример конфигурационного файла
├── run.sh, run.bat      запуск эмулятора
├── Makefile             run / test / demo
└── .gitignore
```

## Коммиты

Каждый этап работы зафиксирован отдельным коммитом по спецификации
Conventional Commits: `feat(stage1)`, `feat(stage2)`, `feat(stage3)`,
`feat(stage4)`, `feat(stage5)`.
