# Балда от Dodo Пиццы

*Тут я буду писать код!! и на Python*

Как-то друг мне показал пост ВКонтакте из паблика Додо Пиццы.  Там говорилось как-то так

> Мы запускаем нашу игру ["Балда"](https://vk.com/app51774407).  В течении (~месяца) за каждый матч вам будут начисляться очки.  Первые ~3 аккаунта в общем рейтинге получат годовой запас Пиццы.

Мой друг предложил мне написать Бота, играющего в их игрушку без вмешательства человека.  Сам он предложил запустить программу на его компе, у меня же чайник совсем, а не комп. Вот спустя неопределённый срок я сел делать бота.

Чего я добился?  При заходе в игру вы можете посмотреть на каком вы месте в ОБЩЕМ рейтинге, а у топ 20 можно посмотреть даже лица.  Так вот.  Я был в этом топе 😎, а на каком месте... Неважно, главное что люди со ВСЕЙ страны заходили и видели мою мордашку. Ну сейчас (я зашёл спустя 3 месяца) я на 29 месте СРЕДИ ВСЕХ АККАУНТОВ ИГРЫ (всего их на момент просмотра 177'000), а я не заходил в игру месяца 4!

Вообще такое количество очков было набрано ЗА ОЧЕНЬ МАЛЕНЬКИЙ СРОК, когда у других было очков где-то миллион, я только об этой игре узнал.  Думаю если я бы сел писать бота чуть пораньше, я бы там всех порвал.

Кстати...  Если представители Додо читают это, то пожалуйста... не убивайте меня.

Окей.  Дальше я буду описывать как я создАл это чудо.  Кстати писать статью я начал в ~июле 2024, спустя 4 месяца после конца Турнира.

Я давно читаю habr.  Статьи где люди пишут код мне ОЧЕНЬ нравятся, я от них прусь.  Только именно у этой статьи есть одна проблема.  Такие статьи интересные только тогда, когда автор описывает не просто буквы, которые он там когда-то напечатал, а когда автор рассказывает о всех трудностях, о всех свалившихся проблемах, когда вместе с автором думаешь над решением задачи.  Так вот, этот пост не такой, ну или вряд ли таким получится, хоть я буду стараться.  Код я писал *ОЧЕНЬ* давно, я нифига не помню, к тому же обладаю скудными навыками в составлении текстов

Ещё скажу, что считаю что мой Бот довольно крут.  Причина этого не в том, что я самовлюбленный, а в том что при разработке Бота и игре в Балду Додо до 3 часов ночи, и играл часто с Ботами.  Что они Боты это ясно.  Например я видел, как в первом раунде были заполнены все буквы, круто, получено где-то 300 очков.  А во втором раунде, Бот просто смотрел на таблицу, получая за Раунд 0.  После мне попадался тот же соперник и заполнял те же клетки те же ми буквами, также ничего не делающий во втором раунде.  Мой бот, напротив, ведёт себя почти как Человек, только набирающий очков в несколько раз больше (ну 2000 за раунд минимум)

Но перед кодом, хотя бы об игре расскажу

## Правила Игры

Идея игры такая (кстати прикольная), советую сыграть.  Вот [ссылка](https://vk.com/app51774407):

1. Вы выбираете слово из 5 букв
2. Вам показывают таблицу 5x5, где в 3 сверху строчке уже вписано выбранное вами слово.  Ваша задача за 3 минуты заполнить эту таблицу буквами, собирая в ней слова.  Слова можно выбирать как в игре Филлворды (почти).  Начиная с любого символа вы можете начать по буквам выделять слово, буквы можете выделять любую соседнюю (слева, справа, снизу, сверху или где-то по-диагонали).  Когда вы соединили буквы и получили слово (существующее), вы получаете за него очки.

![Select a word in the table of letters](./doc/select.jpg "Select a word from letters")

Если за эти 3 минуты вы использовали все буквы в составлении слов, то вы получаете очки умноженные на 2

3. Потом происходит второй раунд, отличающийся лишь тем, что не надо самим заполнять буквы, они уже есть.

Ладно.  Погнали

## Поиск всех слов в таблице

Начинаем с чистого листа. Что дано? Ничего, абсолютно.

Писать я буду на Python, ведь знаю, что такая задача прям будто создана специально для этого языка. Все библиотеки для такого рода задач уже написаны на Python. Плюс его я знаю просто идеально. Все видели (наверное все) видео Хауди Хо, где он реализует какого-нибудь бота-рыбака для Террарии именно на Python, я делаю что-то похожее.

Начинать писать бота я буду с самого простого.  Задача такая:

> дана таблица из букв (5 на 5), найти нужно все возможные слова в этой таблице, причём тупо выводить все слова недостаточно.  Нужно сохранять как-нибудь путь, который позволяет воспроизвести это слово в игре.

Путь буду хранить самым наивным способом: буду сохранять список из координат (каждая координата это кортеж `(x, y)` - координаты буквы в таблице).

Отлично.  Теперь советую вам решить эту задачу в уме самостоятельно.

Надеюсь вы сейчас реально думайте, а не просто читаете это предложение.

Ладно.

Времени было предостаточно, передаём листочки.

Решений было наверное много, наверное даже среди них есть какое-то большое количество хороших.  Но а собственно я как серьёзный программист, решающий *LeetCode*, регулярно участвующий в контестах *Codeforces*, не пропускающий ни одного стрима Tsoding, лично знакомый с Линусом Торвальдсом, участвующий в разработке Манхетанского Проекта(не всему стоит верить на 100%), сразу придумал рабочее решение(возможно оно тупое): я буду просто перебирать ВСЕ комбинации букв, которые только возможно составить.  Возможно вы скажете, что это невозможно... и... будете правы, подвох в том, что я ограничусь только словами из 8 или меньше букв.

Алгоритм такой: буду начинать с ячейки `(i, j)` перебирать все возможные буквы, следующие после этой ячейки, при этом перебирать все возможные ячейки с уже той ячейки, при этом важно не проверять одни и те же буквы несколько раз, поэтому буду поддерживать массив `_used[][]`, где `_used[i][j] == true`, когда букву/ячейку `(i, j)` мы уже используем как часть слова.

Обще это называется dfs, а точнее его разновидность [floodfill](https://usaco.guide/silver/flood-fill?lang=py "я же знаю, что вы не будете на это нажимать")

Ладно.  Все эти понятия, `dfs` (причём он тут, это же не Граф!?).  Вы уже заскучали??  Ничего.  Так и должно быть.  Программисты часто сыпят непонятным терминами, делая вид что только они могут делать свою работу. А вот Марго Робби в пенной ванне попытается вам всё объяснить

![Марго Робби 1](./doc/margo.jpg "Марго Робби 1")

> Любое слово состоит из букв.  А в данном случае, любая буква ещё обладает какой-то координатой в этой таблице.  Левая верхняя буква это `(0, 0)`, нижняя правая это `(0, 4)` или `(4, 0)`.  Какая чёрт его возьми впрочем то разница. `(x, y)` или `(y, x)`!  Кому до этого есть дело.

> Так вот.  Задача стоит простая: найти все возможные пути типа `[(0, 1), (1, 0), (1, 1), ...]`, которые если соединить их по порядку воспроизводят существующее слово.

> Можно перебирать все возможные `(i, j)` это его первый элемент.  Допустим `(i, j) = (0, 0)`, тогда мы можем взять новую букву, это будет либо `(1, 0)` или `(0, 1)`, ну или `(1, 1)`.  Т.е. запускаем три раза сами себя.  Это черт-возьми рекурсия.  Клааас!  Но нужно также сохранять какое слово (строка, `string` ~~типо стринги~~) соответствует данному пути, будем при переходе от буквы к букве добавлять символ ячейки к строке, а если это слово ещё и реальное русское, то сохраняем этот путь (список координат) и говорим что это слово мы уже использовали (вводить одно и тоже слово хоть и несколькими путями бессмысленно — очков всё равно не дадут).  Для первого говорим в начале, что `_used[i][j] = true` (для функций, которые вызываем внутри), а потом возвращаем `_used[i][j] = false` (для функций-родителей)

> Ну что?  Дошло?  А теперь пошли вон

Окей.

Код выглядит таким образом

```python
def _dfs(i, j, path, word: str):
    if i < 0 or i >= n or j < 0 or j >= n:  # заходит за границы, нафиг
        return
    if _used[i][j]:  # если "путь слова" это змейка, то она врезалась в себя же (бля что)
        return

    word += _table[i][j]

    if _is_word_exists(word) and word not in _checked_words:
        _paths.append(path)
        _checked_words.add(word)

    if len(word) == MAX_WORD_LEN:  # MAX_WORD_LEN = 8
        return

    _used[i][j] = True  # следующие вызовы _dfs не будут использовать букву i, j

    for di, dj in _deltas:
        _dfs(i + di, j + dj, path=path + [(i + di, j + dj)], word=word)

    _used[i][j] = False
```

(оригинальный код : по [ссылки](https://github.com/semenInRussia/dodobot/blob/main/src/worder.py "worder.py"))

Здесь `_deltas` это просто список `(di, dj)` величины на которые могут измениться `x` и `y` следующей ячейки

```python
_deltas = [
    (0, -1),  # left
    (0, +1),  # right
    (-1, 0),  # up
    (+1, 0),  # down
    # диагональные
    (+1, -1),  # down-left
    (-1, -1),  # up-left
    (-1, +1),  # up-right
    (+1, +1),  # down-right
]
```

Кстати, функция `_is_word_exists(wrd)` тоже интересная.  Точнее я хотел её сделать такой.  По сути она выглядит так:

```python
def is_word_exists(wrd):
    return wrd in words
```

Где `words` это `set` всех возможных слов, я их храню в отдельном файле `dict.txt` (просто список слов, который я где-то скачал) и читаю в начале программы в `set`.  Ну обще я хотел использовать до этого такую структуру, как Бор (префиксное дерево) (ссылки ищите сами).  Это бы сэкономило кучи памяти, но и так всё норм работает.

Кстати о скорости.  Данный код работает очень быстро, а это же всё-таки Python.  Для меня это стало культурным шоком, я же хотел писать эту часть на C++

Вообще это скучная часть.  Дальше будет интереснее (я надеюсь), но уже сейчас есть хоть какой-нибудь рабочий прототип.  **В ручную** заходите в игру, **В ручную** вводите таблицу, получаете список существующих слов и **сами** выделяете их мышкой.

## Читаем таблицу

Что нужно уметь делать после того, как научились искать слова в таблице?  Не знаю как вы, но я решил почему то научиться читать буквы, которые есть в таблице.  Узнал это, посмотрев историю коммитов, на самом деле очень интересно смотреть как эволюционирует ваш код

Чтение текста, ну как бы не простая задача.  Я решил действовать популярным методом: буду использовать *Tesseract*.  До этого надо уметь делать скриншоты, а на этом останавливаться долго я не буду.  Скажу лишь что для операций над картинками буду юзать `Pillow`, чтобы делать скриншоты, использую `mss`

```python
def screen() -> Image.Image:
    with mss() as s:
        s.shot()
        return Image.open("monitor-1.png")
```

(тут функция возвращает объект `Pillow.Image`, который читает скриншот первого монитора, т.е. читать текст мы будем только при условии, что игра открыта на первом мониторе, с этим проблем не возникло, хоть у друга два монитора)

Таблица выглядит так если что.

![вот таблица с компьютера где стоит специальная операционная система для видеоигр Windows](./doc/playing.1.png)

Если скормить данную картинку Тессеракту, он отработает почти так как и ожидалось.  Т.е. он успешно распознает здесь слова "ВКонтакте", "О нас".  Очевидно, что таблицу (буквы с таблицы) стоит изначально вырезать из данного скриншота.  Делать я это решил самым наивным способом: я просто найду район картинки, где сосредоточены все пиксели цвета текста, благо данный цвет больше нигде в их приложении не используется.  Алгоритм такой: я просто найду минимальный/максимальный `x` и `y` таких пикселей.  (`x0; y0` - минимальные, `x1; y1` - максимальные).  И регион `(x0, y0) x (x1, y1)` - искомый.  Код!

А.  Это тоже не работает, видимо Tesseract'у не хватает такой картинки

![цветная обрезанная таблица](./doc/colored.png)

Для меня такая "тупость" tesseract - шок! Какого фига?  Что я делаю не так?  Где-то я прочитал, что лучше данная фигня будет работать при тёмном тексте на светлом фоне, я решил сделать текст чёрным, а фон белым

```python
def _cvt_img(img: Image.Image) -> Image.Image:
    img = img.crop(_img_box(img))

    # fill text from table with black, other white
    w, h = img.size
    for i in range(w):
        for j in range(h):
            if img.getpixel((i, j)) == TEXT_COLOR:
                img.putpixel((i, j), BLACK)
            else:
                img.putpixel((i, j), WHITE)

    return img

def _img_box(img: Image.Image):
    # find min col and row where table text is started, defaults to
    # maximum possible
    beg_col = w
    beg_row = h

    # the same for col and row where it ended, defaults to min
    # possible
    end_col = 0
    end_row = 0

    for y in range(h):
        for x in range(w):
            if img.getpixel((x, y)) == TEXT_COLOR:
                beg_col = min(beg_col, x)
                beg_row = min(beg_row, y)
                end_col = max(end_col, x)
                end_row = max(end_row, y)

    return beg_col, beg_row, end_col, end_row
```

Замечу, что данный код может не совпадать с действительным, точнее он не совпадает в 100% случаев, здесь немного упрощённая, но рабочая версия

Сейчас из скриншота всего экрана образуется следующая черно-белая фотография:

![черно-белая таблица](./doc/black.png)

Ииии... Это не работает 😓.  Что для меня дикость: Как так? Самая популярная библиотека для распознавания текста, не может понять что тут написано? Как?  Кто её советует?  Сейчас мне конечно ясно, что просто этот шрифт, видимо, не понятен данной нейронке, стоило бы доучить.

Ладно.  Но сегодня же 2024год.  Искусственный интеллект ВЕЗДЕ.  Не ужели я не могу найти нейронку, которая легко "схавает" эту картинку?  И я нашёл - [EasyOCR](https://github.com/JaidedAI/EasyOCR).  Это весьма хорошо натренированная сеть, очень популярная и написана на Python с использованием PyTorch.  Стоп.  PyTorch?  Кто не знает PyTorch это такая очень тяжелая библиотека для написание нейронок.  И когда я говорю тяжёлая, это значит РЕАЛЬНО ТЯЖЁЛАЯ.  За её использование мне пришлось заплатить несколькими гигами свободного места на моём жёстком диске.  Подключив EasyOCR всё заработало почти идеально (пришлось сделать только несколько замен типа 7 => Г, но это всё мелочи).

(кстати потом я решил резать ту черно-белую таблицу на 5 строчек и распознавать каждую отдельно)

Код:

```python
import easyocr
import numpy as np
from PIL import Image

_reader = easyocr.Reader(["ru"])


def extract_table(img: Image.Image, show=False) -> list[str]:
    img = _cvt_img(img, palette)

    if show:
        img.show()

    table = []

    for img_row in split_image_on_rows(img, N):
        row_txt = _remove_whitespaces(row_txt).lower()
        row_txt = row_txt.ljust(N, ".")  # add dots . to make row with needed width
        table.append(row_txt)

    return table


def _remove_whitespaces(s: str):
    return s.replace(" ", "").replace("\n", "")


def _extract_text(img: Image.Image) -> str:
    img = np.array(img)  # type: ignore
    txt = _reader.readtext(img, detail=0)
    txt = "".join(txt)
    txt = (
        txt.replace("0", "о")
        .replace("₽", "р")
        .replace("€", "с")
        .replace("%", "х")
        .replace("3", "з")
        .replace("4", "а")
        .replace("6", "б")
        .replace("7", "п")
    )
    return txt

def split_image_on_rows(img: Image.Image, n: int) -> Iterator[Image.Image]:
    w, h = img.size
    sz = h // n
    for i in range(n):
        # x0, y0, x, y
        yield img.crop((0, sz * i, w, sz * i + sz))
```

Вау!  Сейчас есть что-то на рабочий продукт: я запускаю программу, она делает скрин и ищет все слова, которые есть в таблице.  Но напомню, задача проекта ВЫИГРАТЬ пиццы.  Нужно, чтобы бот работал 24/7, желательно без участия человека, поэтому...

## Автокликинг?

Да, нейминг это сложно.  Это лучшее название для главы, которое я нашёл

Следующую функцию, которую я захотел добавить стала функция самой игры.  То есть ожидается, что буду нажимать на кнопку и бот будет делать всё за нас.  На данный момент хватит того, что бот просто будет выделять слова, которые он сам до этого нашёл.

Идея простая (даже слишком):  найдём область таблицы, в которой находятся все буквы.  После буду просто выделять каждое слово, причём его путь мы знаем (см. функцию `search`).  Осталось написать функцию, которая просто наводит курсор на нужную ячейку по координатам `x` и `y` относительно таблицы.  То есть `(0, 0)` чтобы выделить верхнюю правую ячейку.  Найти `x` и `y` относительно всего экрана тоже довольно легко.  Найду размер одной ячейки (длина таблицы делённая на 5) и перейду к точке (`x0`, `y0` - координаты левого верхнего угла таблицы, `v` и `h` - вертикальный и горизонтальный размер ячейки) `x0 + (i+0.5)*h; y0 + (j+0.5)*v` (`(i, j)` - координаты относительно таблицы)

Здесь ещё стоит добавить некоторые функции, например, двойные очки дадут тогда и только тогда, когда все буквы в таблице были выделены до конца раунда, причём как это произойдёт игра сразу остановится.  Поэтому я сделал несколько вещей, чтобы увеличить "профит":

1. Чтобы быть уверенным, что все буквы могут быть задействованы в игре, я заполню таблицу, так чтобы в каждой её строчке было слово

![слова в таблице, существуют](./doc/colored.png)

2. Чтобы не выйти с раунда раньше его конца(случайно не использовать все буквы задолго до конца раунда), я не буду выделять все слова обладающие буквой в координате `(0, 0)`, тогда будет уверенность что хотя бы одна буква будет не задействована

3. Когда я вижу, что раунд играется столько, что он уже скоро закончится, я сначала выделяю все строчки(которые также существующие слова), а потом начну выделять слова с `(0, 0)`

Это наверное всё

Код буду давать постепенно.  Изначально я создал класс `Gamer`.  На самом деле нет никаких особых причин использовать ООП, но я решил что так как программа будет обладать большим стейтом, то стоит может реализовать всё как методы класса, хоть можно было обойтись проще.  Если посмотрите на мой код, то в нём почти не используется объектно-ориентированная парадигма, почти везде я обхожусь обычными функциями, но сейчас просто захотелось написать так

```python
Rect = tuple[int, int, int, int]

class Gamer:
    ...
```

Во многих функций мне нужен будет текущий(актуальный) скриншот экрана, таблица букв(если есть) и координаты этой таблице.  Добавлю соответственные поля и метод `reset`, чтобы показать что они больше не "свежие"

```python
    _screen: Union[Image.Image, None] = None
    _table: list[str] | None = None
    _table_box: Rect | None = None

    def reset(self) -> None:
        print("reset")
        self._screen = None
        self._table = None
        self._table_box = None
```

Также допишу для них необходимые геттеры.  Кто-то скажит что это какой-то оверинжененг, но на Python я пишу так всегда, для меня такой подход легче.

(идея геттеров возвращать *актуальный* скриншот, таблицу, ....  Если текущие значения полей свежие, то вернуть их.  Иначе пересчитать.  Это удобно, чтобы не делать несколько раз скриншот одного и того же экрана и не передавать `Image.Image` всем нуждающимся функциям)

```python
    @property
    def screen(self) -> Image.Image:
        if self._screen is None:
            self._screen = screen()
        assert self._screen is not None
        return self._screen

    @property
    def table(self) -> list[str]:
        if self._table is None:
            self._extract_table()
        return self._table

    def _extract_table(self) -> None:
        self._table_box = _img_box(self.screen)
        self._table = extract_table(img)

    @property
    def table_box(self) -> Rect:
        if self._table_box is None:
            self._extract_table()
        assert self._table_box is not None
        return self._table_box


```

Несколько второстепенных функций, включая ту которая наводит курсор на нужную ячейку (кстати для неё я использовал Библиотеку `PyAutoGui`, которую могу посоветовать).

```
DURATION = 0.01
import pyautogui as _pg
N = 5

class Gamer:
    # ...

    def _move_cursor_to_cell(self, i: int, j: int) -> None:
        _pg.moveTo(*self._cell_position(i, j), duration=DURATION)

    def _cell_position(self, i: int, j: int) -> tuple[int, int]:
        hsz, vsz = self._cell_sizes
        x0, y0, _, _ = self.table_box
        return (
            int(x0 + (j + 0.5) * hsz),  # x
            int(y0 + (i + 0.5) * vsz),  # y
        )

    @property
    def _cell_sizes(self) -> tuple[int, int]:
        w, h = self.table_image_size
        return w // N, h // N

    @property
    def table_image_size(self) -> tuple[int, int]:
        x0, y0, x1, y1 = self.table_box
        return x1 - x0, y1 - y0
```

следующая функция уже процесс самой игры.  думаю его я описывать подробно не буду, тем более есть комментарии(даже много)

```python
FULL_ROUND_TIME = timedelta(minutes=3)
PLAYING_ROUND_TIME = timedelta(minutes=2, seconds=47)

class Gamer:
    # ...

    def play_round(self) -> None:
        round_start = datetime.now()
        paths = search(self.table)
        last_cell = 0, 0  # cell which bot will visit the last
        last_cell_paths = []

        for p in paths:
            # if playing time is almost over, mark all symbols to do
            # x2
            #
            # strategy to mark ALL symbols is that make rows words and
            # mark them at the end
            round_time = datetime.now() - round_start
            if not row_paths_used and round_time >= PLAYING_ROUND_TIME:
                row_paths_used = True
                self._press_row_paths()

            if round_time >= FULL_ROUND_TIME:
                return

            if last_cell in p:
                last_cell_paths.append(p)
            else:
                self._press_word_path(p)

        if not row_paths_used:
            self._press_row_paths()

        for p in last_cell_paths:
            round_time = datetime.now() - round_start
            if round_time > FULL_ROUND_TIME:
                return
            self._press_word_path(p)


    def _press_word_path(self, path: WordPath):
        """Press a word with the word path at the letter table at the screen."""
        print(f"press a word ({len(path)})")
        self._move_cursor_to_cell(*path[0])
        _pg.mouseDown()
        for i, j in path:
            self._move_cursor_to_cell(i, j)
            _pg.mouseUp()

    def _press_row_paths(self) -> None:
        for p in _row_words_paths():
            self._press_word_path(p)
```

Замечательно! Бот может даже играть

Необходимо правда, ещё научить заполнять его слова.  Это просто.  Для этого создам метод `self.fill()`.  И буду вызывать его в начале `play_round()`

``` python
    def fill(self):
        for i in range(N):
            wrd = next(self._wrds)
            for j, ch in enumerate(wrd):
                self._move_cursor_to_cell(i, j)
                _pg.click()
                _press_rus_char(ch)
```

Как возможно вы видите, необходимо научиться печатать русские буквы.  Додо разрешает делать это при нажатии английских букв, но с Qwerty раскладкой, переводя на Русский.  То есть Qwertyu => Йцукенг, только почему то Додо запрещает таким методом нажимать букву Ё, но да ладно

```python
rus_keyboard = "йцукенгшщзхъфывапролджэячсмитьбю"
eng_keyboard = "qwertyuiop[]asdfghjkl;'zxcvbnm,."
_rus_to_eng = dict(zip(rus_keyboard, eng_keyboard))

def _press_rus_char(ch: str) -> None:
    _pg.press(_rus_to_eng.get(ch, ""))
```

поэтому с `_wrds` (список возможных слов для старта) разобраться можно так:

1. из всех слов оставить пятибуквенные
2. из них убрать все с буквой Ё (потому что её напечатать нереально)

```python
def start_words() -> Iterator[str]:
    sw = list(filter(_is_ok_start_word, worder.words))
    sw = [w for w in worder.words if _is_ok_start_word(w)]

    while True:
        yield from sw

def _is_ok_start_word(w: str) -> bool:
    return len(w) == N and "ё" not in w

```

(вам не обязательно понимать весь код)

и в `Gamer.__init__`:

```python
    def __init__(self):
        self._wrds = start_words()
```

всё

## Автоматизация всего, регулярная перезагрузка, самообучение, обход кое-каких ограничений, неожиданные трудности, результат, пожелания

...

когда я это пишу это предложение.  Файл уже весит 23Кб(без учёта картинок) и содержит 3516слов(до этого предложения).  Я думаю стоит заканчивать.

Всё что есть в `h2` может я допишу во второй части если статья найдёт отклик.  Во потенциальной второй части я расскажу помимо всего прочего о возможно революционном методе создания подобных ботов и о всех подводных камнях.  Но вероятнее статьи не будет.

А пока я прощаюсь!  Напишите коммент о несостоятельности автора!
