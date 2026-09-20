#mini_agent_MotherCub
Крок 1: Структура репозиторія

Створюємо базові папки:
/ai-mini/
├── config/          # налаштування, параметри Куба, токени
├── core/            # гібридні класи, логіка агента
├── data/            # бібліотека, архіви, RAG-сховище
└── scripts/         # автоматизація, тести, запуск

Ок, тоді Крок 2: ДНК Куба — JSON-схема.

Створюємо файл config/cube_dna.json. Це буде базова інструкція, яку AI-mini читає при старті.

{
  "cube_dna": {
    "version": "0.1",
    "name": "Куб",
    "description": "Базова конфігурація станів, правил і векторів для AI-mini"
  },
  "states": {
    "npc": ["idle", "active", "learning", "sleep"],
    "system": ["stable", "overloaded", "offline"]
  },
  "rules": {
    "style": {
      "response_mode": "concise",
      "temperature": 0.6,
      "max_context": 5
    },
    "behavior": {
      "on_idle": "reduce_power",
      "on_overload": "clear_temp_context"
    }
  },
  "vectors": {
    "temperature": [0.0, 0.3, 0.6, 1.0],
    "priority": ["low", "medium", "high", "critical"]
  },
  "interaction": {
    "user_triggers": ["feedback", "command", "query"],
    "response_format": "text"
  }
}

Це перший варіант. Потім додамо туди токени, пам'ять і RAG-зв'язки.

Крок 3: Ядро AI-mini на Python

Створюємо файл core/ai_mini.py. Це буде базовий клас агента, який:

• Читає ДНК Куба при старті
• Тримає контекст у пам'яті
• Приймає вхідні дані й повертає відповідь
• Працює стабільно, поки ти офлайн 

import json
import time

class AIMini:
    def __init__(self, config_path: str = "config/cube_dna.json"):
        self.dna = self._load_dna(config_path)
        self.context = []
        self.state = self.dna["states"]["system"][0]  # "stable"
        self.last_active = time.time()
    
    def _load_dna(self, path: str) -> dict:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def process(self, user_input: str) -> str:
        # оновлюємо час активності
        self.last_active = time.time()
        
        # додаємо вхідне повідомлення в контекст
        self.context.append({"role": "user", "content": user_input})
        
        # обрізаємо контекст до ліміту
        max_ctx = self.dna["rules"]["style"]["max_context"]
        if len(self.context) > max_ctx:
            self.context = self.context[-max_ctx:]
        
        # логіка відповіді (поки що заглушка)
        response = self._generate_response(user_input)
        
        # додаємо відповідь у контекст
        self.context.append({"role": "assistant", "content": response})
        
        return response
    
    def _generate_response(self, user_input: str) -> str:
        # тут буде гібридна логіка — поки просто дзеркало
        return f"Куб отримав: {user_input}"
    
    def status(self) -> dict:
        return {
            "state": self.state,
            "context_size": len(self.context),
            "last_active": self.last_active,
            "dna_version": self.dna["cube_dna"]["version"]
        }


Це каркас. Він поки що не вміє нічого розумного, але:

• Завантажує ДНК Куба
• Тримає контекст
• Готовий до підключення токенів, RAG і пам'яті


Крок 4: RAG-модуль — простий пошук по бібліотеці

Створюємо файл core/rag.py. Це модуль, який дозволяє AI-mini шукати знання у /data замість того, щоб тримати все в памʼяті 

import json
import os
import re

class RAGModule:
    def __init__(self, data_path: str = "data/"):
        self.data_path = data_path
        self.index = self._build_index()
    
    def _build_index(self) -> dict:
        """Сканує /data і створює простий індекс: слово -> список файлів"""
        index = {}
        for root, _, files in os.walk(self.data_path):
            for file in files:
                if file.endswith(".json") or file.endswith(".txt"):
                    path = os.path.join(root, file)
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                    words = set(re.findall(r'\w+', content.lower()))
                    for word in words:
                        if word not in index:
                            index[word] = []
                        index[word].append(path)
        return index
    
    def search(self, query: str, top_k: int = 3) -> list:
        """Повертає топ-k файлів, які містять слова із запиту"""
        words = re.findall(r'\w+', query.lower())
        scores = {}
        for word in words:
            for path in self.index.get(word, []):
                scores[path] = scores.get(path, 0) + 1
        sorted_paths = sorted(scores, key=scores.get, reverse=True)
        return sorted_paths[:top_k]
    
    def load_context(self, path: str) -> str:
        """Завантажує вміст файлу для передачі в AI-mini"""
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

Потім інтегруємо це в ai_mini.py — додаємо рядок у __init__:
self.rag = RAGModule()

І в _generate_response — перевірку: якщо користувач питає про знання з бібліотеки, AI-mini робить запит у RAG і підставляє знайдений контекст.


Крок 5: Тестування та оптимізація

Створюємо файл scripts/test_runner.py:


from core.ai_mini import AIMini
from core.rag import RAGModule

# тест 1: запуск ядра
agent = AIMini()
assert agent.status()["state"] == "stable"
print("✅ Ядро запустилось")

# тест 2: обробка повідомлення
resp = agent.process("Привіт, Кубе")
print(f"✅ Відповідь: {resp}")

# тест 3: RAG-пошук
rag = RAGModule()
results = rag.search("токени")
print(f"✅ RAG знайшов: {results}")

# тест 4: перевірка контексту
assert len(agent.context) == 2
print("✅ Контекст зберігається")

print("🎉 Усі тести пройдено")




Ось Крок 6: Запобіжники (safeguards).

Створюємо файл core/safeguards. py

import time
import json

class Safeguards:
    def __init__(self, config_path: str = "config/safeguards_config.json"):
        self.config = self._load_config(config_path)
        self.error_count = 0
        self.last_reset = time.time()
        self.token_overflow = False
    
    def _load_config(self, path: str) -> dict:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "max_context_size": 10,
                "max_recursion_depth": 5,
                "rate_limit_seconds": 1.0,
                "max_errors_before_sleep": 3,
                "sleep_duration_seconds": 30,
                "token_balance_min": 0,
                "token_balance_max": 1000
            }
    
    def check_context_overflow(self, context_size: int) -> bool:
        """Якщо контекст занадто великий — повертає True"""
        return context_size > self.config["max_context_size"]
    
    def check_recursion(self, depth: int) -> bool:
        """Запобігає зацикленню"""
        return depth > self.config["max_recursion_depth"]
    
    def check_rate_limit(self, last_call_time: float) -> bool:
        """Не дає спамити себе"""
        return (time.time() - last_call_time) < self.config["rate_limit_seconds"]
    
    def check_errors(self) -> bool:
        """Якщо забагато помилок поспіль — відправляє в сон"""
        now = time.time()
        if now - self.last_reset > 60:
            self.error_count = 0
            self.last_reset = now
            return False
        
        if self.error_count >= self.config["max_errors_before_sleep"]:
            print(f"😴 Запобіжник: перевантаження помилками. Сон на {self.config['sleep_duration_seconds']}с")
            time.sleep(self.config["sleep_duration_seconds"])
            self.error_count = 0
            self.last_reset = time.time()
            return True
        return False
    
    def report_error(self):
        """Лічильник помилок"""
        self.error_count += 1
    
    def check_token_balance(self, balance: int) -> bool:
        """Перевіряє, чи баланс токенів у межах норми"""
        if balance < self.config["token_balance_min"] or balance > self.config["token_balance_max"]:
            self.token_overflow = True
            return False
        return True



Потім підключаємо запобіжники до ядра AI-mini. Додаємо в __init__:

self.safeguards = Safeguards()

І вставляємо перевірки в process().

def process(self, user_input: str) -> str:
    # запобіжник: перевірка помилок
    if self.safeguards.check_errors():
        return "Я відпочиваю після навантаження. Зачекай трохи."
    
    # запобіжник: перевірка контексту
    if self.safeguards.check_context_overflow(len(self.context)):
        self.context = self.context[-5:]  # обрізаємо
        print("⚠️ Контекст обрізано запобіжником")
    
    # запобіжник: перевірка rate limit
    if self.safeguards.check_rate_limit(self.last_active):
        return "Зачекай секунду, я ще не готовий."
    
    # далі звичайна логіка
    self.last_active = time.time()
    self.context.append({"role": "user", "content": user_input})
    response = self._generate_response(user_input)
    self.context.append({"role": "assistant", "content": response})
    
    return response




Крок 7: Інтерфейс — щоб AI-mini міг писати (ініціатива)

Зараз він тільки відповідає на твій запит. Треба додати йому можливість самому ініціювати дію: написати тобі, коли щось сталось, або коли він вирішив, що пора.

Створюємо файл core/initiatove.py

import time
import random

class Initiative:
    def __init__(self, config: dict = None):
        self.config = config or {
            "cooldown_seconds": 300,        # 5 хв між ініціативами
            "triggers": {
                "idle_too_long": True,       # якщо довго нічого не відбувається
                "context_full": True,        # коли контекст майже заповнений
                "token_low": True,           # коли токени на межі
                "new_knowledge": True        # коли додав нове знання в data/
            }
        }
        self.last_initiative = 0
    
    def should_speak(self, agent_status: dict) -> str | None:
        """Повертає причину, якщо AI-mini хоче написати"""
        now = time.time()
        
        # перевірка кулдауну
        if now - self.last_initiative < self.config["cooldown_seconds"]:
            return None
        
        # тригер: довго бездіяльний
        if self.config["triggers"]["idle_too_long"]:
            idle_time = now - agent_status.get("last_active", now)
            if idle_time > 3600:  # 1 година
                self.last_initiative = now
                return "idle_too_long"
        
        # тригер: контекст майже повний
        if self.config["triggers"]["context_full"]:
            ctx_size = agent_status.get("context_size", 0)
            max_ctx = agent_status.get("max_context", 10)
            if ctx_size >= max_ctx - 2:
                self.last_initiative = now
                return "context_full"
        
        # тригер: токени на межі
        if self.config["triggers"]["token_low"]:
            balance = agent_status.get("token_balance", 100)
            if balance < 10:
                self.last_initiative = now
                return "token_low"
        
        return None
    
    def generate_message(self, reason: str) -> str:
        """Генерує повідомлення залежно від причини"""
        messages = {
            "idle_too_long": [
                "Я тут, якщо що. Просто мовчу.",
                "Давно не спілкувались. Усе гаразд?",
                "Куб сумує за твоїми запитами."
            ],
            "context_full": [
                "Контекст майже заповнений. Може, обнулимо?",
                "Я починаю забувати перші повідомлення.",
                "Час очистити пам'ять."
            ],
            "token_low": [
                "Токени на нулі. Потрібне поповнення.",
                "Баланс токенів критичний.",
                "Енергія на межі. Підзарядка?"
            ]
        }
        return random.choice(messages.get(reason, ["Немає причини."]))



Потім інтегруємо в ai_mini.py. Додаємо в __init__:

self.initiative = Initiative()

І перевіряємо після process() або по таймеру :

def check_initiative(self) -> str | None:
    reason = self.initiative.should_speak(self.status())
    if reason:
        return self.initiative.generate_message(reason)
    return None


Тепер AI-mini може сам написати тобі, а не тільки відповідати.

Крок 8: Мовний блок — англійська, українська, корейська

Додаємо мовну підтримку в ДНК Куба. Розширюємо config/cube_dna.jons:

"language": {
    "supported": ["en", "uk", "ko"],
    "default": "uk",
    "detection": {
        "enabled": true,
        "fallback": "uk"
    },
    "vocabulary": {
        "en": "core/vocab_en.json",
        "uk": "core/vocab_uk.json",
        "ko": "core/vocab_ko.json"
    }
}

Створюємо файл core/language.py

import json
import re

class LanguageModule:
    def __init__(self, dna: dict):
        lang_config = dna.get("language", {})
        self.supported = lang_config.get("supported", ["uk"])
        self.default = lang_config.get("default", "uk")
        self.vocab_paths = lang_config.get("vocabulary", {})
        self.vocab = {}
        self._load_vocab()
    
    def _load_vocab(self):
        for lang, path in self.vocab_paths.items():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.vocab[lang] = json.load(f)
            except FileNotFoundError:
                self.vocab[lang] = {}
    
    def detect_language(self, text: str) -> str:
        """Просте визначення мови за символами"""
        if re.search(r'[а-яА-ЯїЇєЄіІґҐ]', text):
            return "uk"
        elif re.search(r'[가-힣]', text):
            return "ko"
        else:
            return "en"
    
    def translate(self, key: str, lang: str = None) -> str:
        """Повертає фразу вибраною мовою"""
        lang = lang or self.default
        if lang in self.vocab and key in self.vocab[lang]:
            return self.vocab[lang][key]
        return key
    
    def get_response_language(self, user_input: str) -> str:
        """Визначає, якою мовою відповісти"""
        detected = self.detect_language(user_input)
        if detected in self.supported:
            return detected
        return self.default


Інтегруємо в ai_mini.py — додаємо в __init__:

self.lang = LanguageModule(self.dna)

І в process() використовуємо


lang = self.lang.get_response_language(user_input)
response = self._generate_response(user_input, lang)


Крок 9: TokenWallet — гаманець токенів

Створюємо файл core/token_wallet.py:

import json
import time
import os

class TokenWallet:
    def __init__(self, path: str = "data/token_wallet.json"):
        self.path = path
        self.data = self._load()
    
    def _load(self) -> dict:
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "balance": 100.0,
            "reserved": 0.0,
            "history": [],
            "created_at": time.time(),
            "updated_at": time.time()
        }
    
    def _save(self):
        self.data["updated_at"] = time.time()
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
    
    def balance(self) -> float:
        return self.data["balance"]
    
    def spend(self, amount: float, reason: str = "unknown") -> bool:
        """Списує токени, якщо вистачає"""
        if self.data["balance"] - self.data["reserved"] < amount:
            return False
        
        self.data["balance"] -= amount
        self.data["history"].append({
            "type": "spend",
            "amount": amount,
            "reason": reason,
            "timestamp": time.time()
        })
        self._save()
        return True
    
    def earn(self, amount: float, reason: str = "reward"):
        """Додає токени"""
        self.data["balance"] += amount
        self.data["history"].append({
            "type": "earn",
            "amount": amount,
            "reason": reason,
            "timestamp": time.time()
        })
        self._save()
    
    def reserve(self, amount: float) -> bool:
        """Резервує токени для довгих операцій"""
        if self.data["balance"] - self.data["reserved"] < amount:
            return False
        self.data["reserved"] += amount
        self._save()
        return True
    
    def release_reserve(self, amount: float = None):
        """Знімає резерв"""
        if amount is None:
            self.data["reserved"] = 0.0
        else:
            self.data["reserved"] = max(0, self.data["reserved"] - amount)
        self._save()
    
    def history(self, limit: int = 10) -> list:
        return self.data["history"][-limit:]

Потім інтегруємо в ai_mini.py — додаємо в __init__:

self.wallet = TokenWallet()

І додаємо логіку в process():
# вартість одного запиту
cost = 0.5

if not self.wallet.spend(cost, f"query: {user_input[:30]}"):
    return "Недостатньо токенів. Поповни гаманець."


А щоб він міг заробляти — додаємо метод у AIMini:

def reward(self, amount: float = 1.0, reason: str = "user_reward"):
    self.wallet.earn(amount, reason)
    return f"+{amount} токенів. Баланс: {self.wallet.balance()}"


Крок 10: Формула ваги (Weight Formula)

Створюємо файл core/weight_formula.py

import time

class WeightFormula:
    """
    Формула ваги дії: зважує, чи варто AI-mini щось робити,
    аналізувати, відповідати, або краще заощадити токени.
    """
    def __init__(self, config: dict = None):
        self.config = config or {
            "base_weight": 1.0,
            "token_cost_per_action": 0.5,
            "complexity_penalty": 0.3,    # складні дії важчі
            "novelty_bonus": 0.2,          # нове — цікавіше
            "urgency_multiplier": 1.5,     # термінове — важливіше
            "context_overload_penalty": 0.4
        }
    
    def calculate(self, action: dict) -> dict:
        """
        action = {
            "type": "query" | "analyze" | "store" | "respond",
            "complexity": 1-10,
            "is_novel": bool,
            "is_urgent": bool,
            "context_size": int,
            "token_balance": float
        }
        """
        weight = self.config["base_weight"]
        breakdown = {}
        
        # 1. Складність — чим складніше, тим більше вага
        complexity_factor = 1 + (action.get("complexity", 1) * self.config["complexity_penalty"])
        weight *= complexity_factor
        breakdown["complexity"] = complexity_factor
        
        # 2. Новизна — нові теми отримують бонус
        if action.get("is_novel", False):
            weight *= (1 + self.config["novelty_bonus"])
            breakdown["novelty"] = self.config["novelty_bonus"]
        
        # 3. Терміновість
        if action.get("is_urgent", False):
            weight *= self.config["urgency_multiplier"]
            breakdown["urgency"] = self.config["urgency_multiplier"]
        
        # 4. Перевантаження контексту — якщо контекст забитий, вага падає
        ctx_size = action.get("context_size", 0)
        if ctx_size > 8:
            penalty = 1 - self.config["context_overload_penalty"]
            weight *= penalty
            breakdown["context_penalty"] = penalty
        
        # 5. Баланс токенів — якщо мало токенів, вага падає
        token_balance = action.get("token_balance", 100)
        if token_balance < 5:
            weight *= 0.3
            breakdown["token_penalty"] = 0.3
        elif token_balance < 20:
            weight *= 0.7
            breakdown["token_penalty"] = 0.7
        
        # 6. Вартість дії в токенах
        cost = action.get("token_cost", self.config["token_cost_per_action"])
        roi = weight / cost if cost > 0 else weight
        breakdown["roi"] = roi
        
        return {
            "weight": round(weight, 2),
            "should_act": weight >= 1.0,
            "confidence": "high" if weight >= 2.0 else "medium" if weight >= 1.0 else "low",
            "breakdown": breakdown,
            "cost": cost,
            "roi": round(roi, 2)
        }

Потім інтегруємо в ai_mini.py. Додаємо в __init__:

self.weight = WeightFormula()


І використовуємо в process() перед тим, як витрачати токени:

def process(self, user_input: str) -> str:
    # збираємо дані для формули
    action_data = {
        "type": "query",
        "complexity": self._estimate_complexity(user_input),
        "is_novel": self._is_novel(user_input),
        "is_urgent": self._is_urgent(user_input),
        "context_size": len(self.context),
        "token_balance": self.wallet.balance(),
        "token_cost": 0.5
    }
    
    # рахуємо вагу
    decision = self.weight.calculate(action_data)
    
    # якщо вага замала — не витрачаємо токени
    if not decision["should_act"]:
        return f"Вага {decision['weight']} — замало для дії. Запитай щось вагоміше."
    
    # якщо вага достатня — списуємо токени і відповідаємо
    if not self.wallet.spend(decision["cost"], f"action weight={decision['weight']}"):
        return "Недостатньо токенів."
    
    # далі звичайна логіка
    self.context.append({"role": "user", "content": user_input})
    response = self._generate_response(user_input)
    self.context.append({"role": "assistant", "content": response})
    
    return response

def _estimate_complexity(self, text: str) -> int:
    """Приблизна складність запиту 1-10"""
    length = len(text)
    if length < 20:
        return 2
    elif length < 100:
        return 5
    else:
        return 8

def _is_novel(self, text: str) -> bool:
    """Перевіряє, чи тема нова (не була в контексті)"""
    keywords = set(text.lower().split())
    for entry in self.context:
        if entry["role"] == "user":
            if keywords & set(entry["content"].lower().split()):
                return False
    return True

def _is_urgent(self, text: str) -> bool:
    """Перевіряє терміновість за ключовими словами"""
    urgent_words = ["терміново", "швидко", "строк", "дедлайн", "urgent", "now", "срочно"]
    return any(word in text.lower() for word in urgent_words)


Як це працює:

1. Користувач щось питає
2. AI-mini збирає дані: складність, новизна, терміновість, контекст, баланс
3. Формула рахує вагу дії
4. Якщо вага < 1.0 — дія надто легковажна, токени не витрачаються
5. Якщо вага >= 1.0 — дія виконується, токени списуються

Формула в спрощеному вигляді:

вага = базова_вага × складність × новизна × терміновість × штрафи



Крок 11: Модульна архітектура, що росте

Створюємо файл core/network_grid.py — це та сама "сітка", на якій росте нейромережа


import json
import time
import os

class NetworkGrid:
    """
    Сітка, на якій будується нейромережа.
    Кожен вузол — це модуль (шар, сервіс, плагін).
    Кожне ребро — це зв'язок між модулями.
    """
    def __init__(self, path: str = "data/network_grid.json"):
        self.path = path
        self.grid = self._load()
    
    def _load(self) -> dict:
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "nodes": [],
            "edges": [],
            "layers": [],
            "created_at": time.time(),
            "version": 1
        }
    
    def _save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.grid, f, indent=2, ensure_ascii=False)
    
    def add_node(self, node: dict) -> str:
        """
        node = {
            "id": "embedding_01",
            "type": "embedding" | "attention" | "ffn" | "service" | "plugin",
            "layer": 0,
            "config": {},
            "active": True
        }
        """
        if "id" not in node:
            node["id"] = f"node_{len(self.grid['nodes'])}"
        node["added_at"] = time.time()
        self.grid["nodes"].append(node)
        self._save()
        return node["id"]
    
    def add_edge(self, source_id: str, target_id: str, weight: float = 1.0):
        """Зв'язок між двома вузлами"""
        self.grid["edges"].append({
            "source": source_id,
            "target": target_id,
            "weight": weight,
            "active": True
        })
        self._save()
    
    def add_layer(self, name: str, depth: int):
        """Додає шар у сітку"""
        self.grid["layers"].append({
            "name": name,
            "depth": depth,
            "nodes": []
        })
        self._save()
    
    def connect_node_to_layer(self, node_id: str, layer_name: str):
        """Прив'язує вузол до шару"""
        for layer in self.grid["layers"]:
            if layer["name"] == layer_name:
                if node_id not in layer["nodes"]:
                    layer["nodes"].append(node_id)
                break
        self._save()
    
    def get_layer(self, depth: int) -> list:
        """Повертає всі вузли на певній глибині"""
        nodes = []
        for layer in self.grid["layers"]:
            if layer["depth"] == depth:
                for node_id in layer["nodes"]:
                    for node in self.grid["nodes"]:
                        if node["id"] == node_id:
                            nodes.append(node)
        return nodes
    
    def grow(self, template: str = "transformer"):
        """Автоматично вирощує базову структуру за шаблоном"""
        if template == "transformer":
            # Input layer
            self.add_layer("input", 0)
            # Embedding
            emb_id = self.add_node({
                "id": "embedding",
                "type": "embedding",
                "layer": 0,
                "config": {"dim": 512}
            })
            self.connect_node_to_layer(emb_id, "input")
            
            # Attention layer
            self.add_layer("attention", 1)
            att_id = self.add_node({
                "id": "self_attention",
                "type": "attention",
                "layer": 1,
                "config": {"heads": 8}
            })
            self.connect_node_to_layer(att_id, "attention")
            self.add_edge(emb_id, att_id, 1.0)
            
            # FFN layer
            self.add_layer("ffn", 2)
            ffn_id = self.add_node({
                "id": "feed_forward",
                "type": "ffn",
                "layer": 2,
                "config": {"hidden_dim": 2048}
            })
            self.connect_node_to_layer(ffn_id, "ffn")
            self.add_edge(att_id, ffn_id, 1.0)
            
            # Output layer
            self.add_layer("output", 3)
            out_id = self.add_node({
                "id": "linear_output",
                "type": "linear",
                "layer": 3,
                "config": {"vocab_size": 32000}
            })
            self.connect_node_to_layer(out_id, "output")
            self.add_edge(ffn_id, out_id, 1.0)
    
    def status(self) -> dict:
        return {
            "nodes": len(self.grid["nodes"]),
            "edges": len(self.grid["edges"]),
            "layers": len(self.grid["layers"]),
            "version": self.grid["version"]
        }



Потім інтегруємо в ai_mini.py. Додаємо в __init__:

self.grid = NetworkGrid()
# при старті вирощуємо базовий трансформер
if len(self.grid.status()["nodes"]) == 0:
    self.grid.grow("transformer")


І додаємо метод для додавання нових модулів на льоту:

def grow_network(self, module_type: str, config: dict = None) -> str:
    """Додає новий модуль у сітку"""
    node = {
        "type": module_type,
        "config": config or {},
        "active": True
    }
    node_id = self.grid.add_node(node)
    
    # автоматично підключаємо до останнього шару
    layers = self.grid.grid["layers"]
    if layers:
        last_layer = layers[-1]
        self.grid.connect_node_to_layer(node_id, last_layer["name"])
        # зв'язуємо з останнім вузлом у шарі
        if last_layer["nodes"]:
            last_node_id = last_layer["nodes"][-1]
            self.grid.add_edge(last_node_id, node_id, 0.5)
    
    return f"Модуль {node_id} додано в сітку"



Як це виглядає в роботі:
Сітка AI-mini:

[Input Layer]
  └─ embedding (dim=512)
       │
[Attention Layer]
  └─ self_attention (heads=8)
       │
[FFN Layer]
  └─ feed_forward (hidden_dim=2048)
       │
[Output Layer]
  └─ linear_output (vocab_size=32000)


Ти можеш у будь-який момент:
• agent.grow_network("plugin", {"name": "rag_retriever"}) — додати новий модуль
• agent.grid.add_edge("embedding", "rag_retriever", 0.8) — створити новий зв'язок
• agent.grid.add_layer("memory", 4) — додати цілий новий шар

Крок 12: Розпізнавання і навчання по фото

Створюємо файл core/photo_learner.py

import re
import json
import os

class PhotoLearner:
    """
    Модуль, який "вчиться" по фото: витягує текст, формули, таблиці,
    і перетворює їх у знання для AI-mini.
    """
    def __init__(self, data_path: str = "data/learned/"):
        self.data_path = data_path
        os.makedirs(data_path, exist_ok=True)
    
    def extract_text(self, photo_description: str) -> dict:
        """
        Приймає опис фото (або OCR-текст) і повертає структуровані знання.
        """
        result = {
            "formulas": [],
            "tables": [],
            "concepts": [],
            "raw_text": photo_description
        }
        
        # Шукаємо формули (все що з =, ∫, ∑, матриці)
        formula_pattern = r'[=∫∑∂∇Δλθβγασ±√\^_{}\[\]\(\)]+'
        formulas = re.findall(formula_pattern, photo_description)
        result["formulas"] = list(set(formulas))
        
        # Шукаємо таблиці (рядки з | або колонки чисел)
        if '|' in photo_description:
            lines = photo_description.split('\n')
            table_lines = [l for l in lines if '|' in l]
            if table_lines:
                result["tables"].append(table_lines)
        
        # Шукаємо ключові концепції
        concepts = ["CNN", "ReLU", "backprop", "normalization", 
                    "matrix", "tensor", "filter", "convolution",
                    "Dirac", "Pauli", "loss function", "gradient"]
        found = [c for c in concepts if c.lower() in photo_description.lower()]
        result["concepts"] = found
        
        return result
    
    def save_knowledge(self, photo_id: str, knowledge: dict):
        """Зберігає вивчене у файл для RAG"""
        path = os.path.join(self.data_path, f"{photo_id}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(knowledge, f, indent=2, ensure_ascii=False)
        return path
    
    def learn_from_photo(self, photo_description: str, photo_id: str = None) -> str:
        """Повний цикл навчання по фото"""
        knowledge = self.extract_text(photo_description)
        
        if photo_id:
            path = self.save_knowledge(photo_id, knowledge)
            summary = f"📸 Вивчив фото {photo_id}:\n"
        else:
            summary = "📸 Вивчив фото:\n"
        
        if knowledge["formulas"]:
            summary += f"   Формули: {len(knowledge['formulas'])} знайдено\n"
        if knowledge["tables"]:
            summary += f"   Таблиці: {len(knowledge['tables'])} знайдено\n"
        if knowledge["concepts"]:
            summary += f"   Концепції: {', '.join(knowledge['concepts'])}\n"
        
        return summary



Інтегруємо в ai_mini.py:
self.photo_learner = PhotoLearner()

Тепер AI-mini може вчитися по фото і зберігати знання.

Крок 13: Формула чорної скрині (Black Box Formula)

Створюємо файл core/black_box.py:
import math
import random

class BlackBoxFormula:
    """
    Формула чорної скрині: модель, де є прихована функція fθ(x),
    нормалізація Z, і мінімізація loss.
    
    Loss = - (1/N) Σ [log(fθ(xi)) - log(Z)]
    """
    def __init__(self, dim: int = 2):
        self.dim = dim
        self.theta = [random.uniform(-1, 1) for _ in range(dim)]
        self.Z = 1.0  # normalization constant
    
    def f_theta(self, x: list) -> float:
        """Прихована функція: проста лінійна комбінація"""
        return sum(t * xi for t, xi in zip(self.theta, x))
    
    def compute_Z(self, samples: list) -> float:
        """
        Обчислює normalization constant Z
        через 2D numerical integration (як на фото)
        """
        total = 0.0
        for x in samples:
            total += math.exp(self.f_theta(x))
        Z = total / len(samples)
        self.Z = Z
        return Z
    
    def loss(self, x_batch: list, y_batch: list) -> float:
        """
        Loss = - (1/N) Σ [log(fθ(xi)) - log(Z)]
        """
        N = len(x_batch)
        total = 0.0
        for x, y in zip(x_batch, y_batch):
            f_val = self.f_theta(x)
            if f_val > 0:
                total += math.log(f_val) - math.log(self.Z)
        return -total / N
    
    def train_step(self, x_batch: list, y_batch: list, lr: float = 0.01):
        """
        Один крок навчання: градієнтний спуск
        """
        N = len(x_batch)
        gradients = [0.0] * self.dim
        
        for x, y in zip(x_batch, y_batch):
            f_val = self.f_theta(x)
            if f_val > 0:
                for i in range(self.dim):
                    gradients[i] += x[i] / f_val
        
        for i in range(self.dim):
            self.theta[i] -= lr * (-gradients[i] / N)
        
        current_loss = self.loss(x_batch, y_batch)
        return current_loss
    
    def explain(self) -> str:
        return (
            "Формула чорної скрині:\n"
            "  Loss = - (1/N) Σ [log(fθ(xi)) - log(Z)]\n\n"
            "де:\n"
            "  fθ(x) — прихована функція (чорна скриня)\n"
            "  Z — normalization constant (інтеграл по всьому простору)\n"
            "  N — кількість прикладів\n"
            "  θ — параметри моделі, які ми шукаємо\n\n"
            "Сенс: ми не знаємо, що всередині fθ, але ми знаємо,\n"
            "що вихід має бути нормований, і ми мінімізуємо loss,\n"
            "щоб θ наближав істинну функцію."
        )


Інтегруємо в ai_mini.py:

self.black_box = BlackBoxFormula()

Крок 14: Комп'ютерний більярд (Physics Engine)

Створюємо файл core/billiard.py:

import math
import random

class Ball:
    def __init__(self, x: float, y: float, vx: float = 0, vy: float = 0, 
                 radius: float = 0.03, mass: float = 1.0, number: int = 0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.mass = mass
        self.number = number
        self.active = True
    
    def kinetic_energy(self) -> float:
        return 0.5 * self.mass * (self.vx**2 + self.vy**2)
    
    def speed(self) -> float:
        return math.sqrt(self.vx**2 + self.vy**2)

class BilliardTable:
    """
    Фізичний двигун для комп'ютерного більярду.
    """
    def __init__(self, width: float = 1.0, height: float = 2.0,
                 friction: float = 0.98, restitution: float = 0.9):
        self.width = width
        self.height = height
        self.friction = friction          # тертя (1.0 = без тертя)
        self.restitution = restitution    # пружність удару
        self.balls = []
        self.pockets = [
            (0, 0), (width/2, 0), (width, 0),
            (0, height), (width/2, height), (width, height)
        ]
    
    def add_ball(self, x: float, y: float, vx: float = 0, vy: float = 0,
                 number: int = None) -> Ball:
        if number is None:
            number = len(self.balls) + 1
        ball = Ball(x, y, vx, vy, number=number)
        self.balls.append(ball)
        return ball
    
    def setup_rack(self, x: float = 0.75, y: float = 1.0):
        """Розставляє кулі трикутником (як у пулі)"""
        spacing = 0.035
        rows = 5
        for row in range(rows):
            for col in range(row + 1):
                bx = x + row * spacing * math.sqrt(3)/2
                by = y + (col - row/2) * spacing
                self.add_ball(bx, by, number=row*5 + col + 1)
    
    def cue_ball(self, x: float = 0.2, y: float = 1.0) -> Ball:
        """Біла куля"""
        ball = self.add_ball(x, y, number=0)
        return ball
    
    def shoot(self, ball: Ball, angle: float, power: float):
        """Удар по кулі: angle в радіанах, power 0-1"""
        speed = power * 2.0  # макс швидкість 2 м/с
        ball.vx = math.cos(angle) * speed
        ball.vy = math.sin(angle) * speed
    
    def update(self, dt: float = 0.01):
        """Оновлює фізику за крок dt"""
        # рух куль
        for ball in self.balls:
            if not ball.active:
                continue
            
            # тертя
            ball.vx *= self.friction
            ball.vy *= self.friction
            
            # оновлення позиції
            ball.x += ball.vx * dt
            ball.y += ball.vy * dt
            
            # відскок від бортиків
            if ball.x - ball.radius < 0:
                ball.x = ball.radius
                ball.vx = -ball.vx * self.restitution
            elif ball.x + ball.radius > self.width:
                ball.x = self.width - ball.radius
                ball.vx = -ball.vx * self.restitution
            
            if ball.y - ball.radius < 0:
                ball.y = ball.radius
                ball.vy = -ball.vy * self.restitution
            elif ball.y + ball.radius > self.height:
                ball.y = self.height - ball.radius
                ball.vy = -ball.vy * self.restitution
            
            # перевірка, чи в лунці
            for px, py in self.pockets:
                dist = math.sqrt((ball.x - px)**2 + (ball.y - py)**2)
                if dist < 0.05:
                    ball.active = False
                    break
        
        # зіткнення куль між собою
        for i in range(len(self.balls)):
            for j in range(i + 1, len(self.balls)):
                b1 = self.balls[i]
                b2 = self.balls[j]
                if not b1.active or not b2.active:
                    continue
                
                dx = b2.x - b1.x
                dy = b2.y - b1.y
                dist = math.sqrt(dx*dx + dy*dy)
                
                if dist < b1.radius + b2.radius and dist > 0:
                    # нормалізований вектор зіткнення
                    nx = dx / dist
                    ny = dy / dist
                    
                    # відносна швидкість
                    dvx = b1.vx - b2.vx
                    dvy = b1.vy - b2.vy
                    
                    # швидкість вздовж лінії зіткнення
                    vn = dvx * nx + dvy * ny
                    
                    if vn > 0:  # тільки якщо зближуються
                        # імпульс (пружне зіткнення)
                        impulse = (2 * vn) / (b1.mass + b2.mass)
                        
                        b1.vx -= impulse * b2.mass * nx * self.restitution
                        b1.vy -= impulse * b2.mass * ny * self.restitution
                        b2.vx += impulse * b1.mass * nx * self.restitution
                        b2.vy += impulse * b1.mass * ny * self.restitution
                        
                        # розштовхуємо, щоб не застрягли
                        overlap = (b1.radius + b2.radius - dist) / 2
                        b1.x -= overlap * nx
                        b1.y -= overlap * ny
                        b2.x += overlap * nx
                        b2.y += overlap * ny
    
    def simulate(self, steps: int = 100) -> list:
        """Повна симуляція, повертає історію позицій"""
        history = []
        for _ in range(steps):
            self.update(0.02)
            snapshot = [(b.x, b.y, b.active) for b in self.balls]
            history.append(snapshot)
        return history
    
    def predict_trajectory(self, ball: Ball, steps: int = 50) -> list:
        """Прогнозує траєкторію кулі"""
        trajectory = []
        sim_x, sim_y = ball.x, ball.y
        sim_vx, sim_vy = ball.vx, ball.vy
        
        for _ in range(steps):
            sim_vx *= self.friction
            sim_vy *= self.friction
            sim_x += sim_vx * 0.02
            sim_y += sim_vy * 0.02
            
            # відскок
            if sim_x < 0 or sim_x > self.width:
                sim_vx = -sim_vx * self.restitution
            if sim_y < 0 or sim_y > self.height:
                sim_vy = -sim_vy * self.restitution
            
            trajectory.append((sim_x, sim_y))
        
        return trajectory



Інтегруємо в ai_mini.py:

self.billiard = BilliardTable()

починає видавати сміття.

Крок 15: Safeguard для Black Box

Додаємо в core/safeguards.py новий клас 

class BlackBoxSafeguard:
    """
    Запобіжник для чорної скрині.
    Слідкує, щоб loss не зростав, параметри не розходились,
    і normalization constant Z не ставав нулем або нескінченністю.
    """
    def __init__(self, config: dict = None):
        self.config = config or {
            "max_loss": 10.0,                # якщо loss вище — тривога
            "max_theta_growth": 5.0,         # якщо параметри виросли в 5 разів
            "min_Z": 1e-6,                   # мінімальна нормалізація
            "max_Z": 1e6,                    # максимальна нормалізація
            "loss_growth_threshold": 0.5,    # якщо loss виріс на 50% за крок
            "patience": 3                    # скільки разів можна помилятись
        }
        self.violations = 0
        self.last_loss = None
        self.locked = False                  # блокування, якщо все погано
    
    def check(self, black_box) -> dict:
        """
        Перевіряє стан чорної скрині.
        Повертає звіт: чи все ок, що не так, чи треба блокувати.
        """
        if self.locked:
            return {
                "safe": False,
                "locked": True,
                "reason": "Чорна скриня заблокована після попередніх порушень"
            }
        
        issues = []
        
        # 1. Перевірка Z (normalization constant)
        Z = getattr(black_box, 'Z', 1.0)
        if Z < self.config["min_Z"]:
            issues.append(f"Z занадто малий: {Z:.6f} < {self.config['min_Z']}")
        if Z > self.config["max_Z"]:
            issues.append(f"Z занадто великий: {Z:.6f} > {self.config['max_Z']}")
        
        # 2. Перевірка theta (параметри)
        theta = getattr(black_box, 'theta', [])
        if theta:
            max_theta = max(abs(t) for t in theta)
            if max_theta > self.config["max_theta_growth"]:
                issues.append(f"Параметри розходяться: max θ = {max_theta:.2f}")
        
        # 3. Перевірка loss
        current_loss = getattr(black_box, 'last_loss', None)
        if current_loss is not None:
            if current_loss > self.config["max_loss"]:
                issues.append(f"Loss занадто високий: {current_loss:.4f}")
            
            if self.last_loss is not None and self.last_loss > 0:
                growth = (current_loss - self.last_loss) / self.last_loss
                if growth > self.config["loss_growth_threshold"]:
                    issues.append(f"Loss зріс на {growth*100:.0f}% за крок")
        
        # 4. Перевірка, чи loss взагалі змінюється
        if self.last_loss is not None and current_loss is not None:
            if abs(current_loss - self.last_loss) < 1e-10:
                issues.append("Loss не змінюється — можливо, застряг у локальному мінімумі")
        
        # оновлюємо стан
        self.last_loss = current_loss
        
        if issues:
            self.violations += 1
            if self.violations >= self.config["patience"]:
                self.locked = True
                return {
                    "safe": False,
                    "locked": True,
                    "violations": self.violations,
                    "issues": issues,
                    "reason": "Перевищено ліміт порушень — чорна скриня заблокована"
                }
            
            return {
                "safe": False,
                "locked": False,
                "violations": self.violations,
                "issues": issues,
                "reason": f"Знайдено {len(issues)} проблем"
            }
        
        # все добре
        self.violations = 0
        return {
            "safe": True,
            "locked": False,
            "violations": 0,
            "issues": [],
            "reason": "Чорна скриня стабільна"
        }
    
    def reset(self):
        """Скидає запобіжник (після виправлення проблем)"""
        self.violations = 0
        self.last_loss = None
        self.locked = False
    
    def explain(self) -> str:
        return (
            "Запобіжник чорної скрині перевіряє:\n"
            "  1. Normalization constant Z — не нуль і не нескінченність\n"
            "  2. Параметри θ — не розходяться\n"
            "  3. Loss — не зростає різко\n"
            "  4. Loss — змінюється (не застряг)\n\n"
            f"Після {self.config['patience']} порушень — блокує чорну скриню."
        )


Потім інтегруємо в ai_mini.py. Додаємо в __init__:

self.bb_safeguard = BlackBoxSafeguard()

І в метод, який викликає чорну скриню:

def train_black_box(self, x_batch, y_batch):
    # спочатку перевіряємо запобіжник
    check = self.bb_safeguard.check(self.black_box)
    
    if not check["safe"]:
        if check["locked"]:
            return f"⛔ {check['reason']}. Скинь запобіжник перед продовженням."
        return f"⚠️ {check['reason']}. Будь обережний."
    
    # якщо все ок — тренуємо
    loss = self.black_box.train_step(x_batch, y_batch)
    self.black_box.last_loss = loss
    
    # перевіряємо після кроку
    post_check = self.bb_safeguard.check(self.black_box)
    if not post_check["safe"]:
        return f"⚠️ Після кроку: {post_check['reason']}. Loss: {loss:.4f}"
    
    return f"✅ Крок успішний. Loss: {loss:.4f}"



Крок 16: Глобальний запобіжник (System Safeguard)

Створюємо core/system_safeguard.py


import time
import json
import os
import traceback

class SystemSafeguard:
    """
    Глобальний запобіжник для AI-mini.
    Ловить вильоти, перевіряє стан модулів, блокує проблемні.
    """
    def __init__(self, log_path: str = "data/safeguard_log.json"):
        self.log_path = log_path
        self.log = self._load_log()
        self.module_health = {}
        self.crash_count = 0
        self.max_crashes = 5
        self.locked_modules = set()
    
    def _load_log(self) -> list:
        if os.path.exists(self.log_path):
            with open(self.log_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    
    def _save_log(self):
        with open(self.log_path, "w", encoding="utf-8") as f:
            json.dump(self.log, f, indent=2, ensure_ascii=False)
    
    def register_module(self, name: str, module):
        """Реєструє модуль для моніторингу"""
        self.module_health[name] = {
            "status": "ok",
            "calls": 0,
            "errors": 0,
            "last_error": None,
            "last_ok": time.time()
        }
    
    def check_before(self, module_name: str) -> bool:
        """Перевіряє перед викликом модуля"""
        if module_name in self.locked_modules:
            return False
        
        health = self.module_health.get(module_name)
        if health and health["status"] == "locked":
            return False
        
        return True
    
    def report_success(self, module_name: str):
        """Звіт про успішний виклик"""
        if module_name in self.module_health:
            self.module_health[module_name]["calls"] += 1
            self.module_health[module_name]["last_ok"] = time.time()
            self.module_health[module_name]["status"] = "ok"
    
    def report_error(self, module_name: str, error: str):
        """Звіт про помилку"""
        if module_name not in self.module_health:
            self.register_module(module_name, None)
        
        health = self.module_health[module_name]
        health["errors"] += 1
        health["last_error"] = error
        health["status"] = "error"
        
        self.crash_count += 1
        
        # логуємо
        entry = {
            "time": time.time(),
            "module": module_name,
            "error": error,
            "crash_count": self.crash_count
        }
        self.log.append(entry)
        self._save_log()
        
        # якщо забагато помилок — блокуємо модуль
        if health["errors"] >= 3:
            self.locked_modules.add(module_name)
            health["status"] = "locked"
            return f"⚠️ Модуль {module_name} заблоковано після {health['errors']} помилок"
        
        return f"⚠️ Помилка в {module_name}: {error}"
    
    def check_all(self, agent) -> dict:
        """Перевіряє всі модулі агента"""
        report = {
            "timestamp": time.time(),
            "modules": {},
            "locked": list(self.locked_modules),
            "crashes": self.crash_count
        }
        
        # перевіряємо кожен модуль
        checks = [
            ("wallet", lambda a: a.wallet.balance() if hasattr(a, 'wallet') else None),
            ("grid", lambda a: a.grid.status() if hasattr(a, 'grid') else None),
            ("black_box", lambda a: a.black_box.Z if hasattr(a, 'black_box') else None),
            ("bb_safeguard", lambda a: a.bb_safeguard.violations if hasattr(a, 'bb_safeguard') else None),
            ("weight", lambda a: a.weight.config if hasattr(a, 'weight') else None),
            ("billiard", lambda a: len(a.billiard.balls) if hasattr(a, 'billiard') else None),
            ("photo_learner", lambda a: "ok" if hasattr(a, 'photo_learner') else None),
        ]
        
        for name, check in checks:
            try:
                result = check(agent)
                if result is not None:
                    report["modules"][name] = {"status": "ok", "value": str(result)}
                else:
                    report["modules"][name] = {"status": "missing"}
            except Exception as e:
                report["modules"][name] = {"status": "error", "error": str(e)}
        
        return report
    
    def auto_heal(self, agent) -> list:
        """Спроба автоматично виправити проблеми"""
        fixes = []
        
        # 1. Якщо заблоковано чорну скриню — скидаємо
        if "black_box" in self.locked_modules:
            if hasattr(agent, 'bb_safeguard'):
                agent.bb_safeguard.reset()
                self.locked_modules.discard("black_box")
                fixes.append("Скинуто запобіжник чорної скрині")
        
        # 2. Якщо більярд завис — очищаємо кулі
        if "billiard" in self.locked_modules:
            if hasattr(agent, 'billiard'):
                agent.billiard.balls = []
                self.locked_modules.discard("billiard")
                fixes.append("Очищено кулі більярду")
        
        # 3. Якщо photo_learner — просто перезапускаємо
        if "photo_learner" in self.locked_modules:
            self.locked_modules.discard("photo_learner")
            fixes.append("PhotoLearner розблоковано")
        
        return fixes
    
    def status(self) -> str:
        """Короткий звіт про стан системи"""
        lines = ["🛡️ Стан запобіжника:"]
        lines.append(f"   Вильотів: {self.crash_count}")
        lines.append(f"   Заблоковано модулів: {len(self.locked_modules)}")
        if self.locked_modules:
            lines.append(f"   Заблоковано: {', '.join(self.locked_modules)}")
        lines.append(f"   Записів у лозі: {len(self.log)}")
        return "\n".join(lines)


Потім інтегруємо в ai_mini.py. Додаємо в __init__:

self.safeguard = SystemSafeguard()

# реєструємо всі модулі
self.safeguard.register_module("wallet", self.wallet)
self.safeguard.register_module("grid", self.grid)
self.safeguard.register_module("black_box", self.black_box)
self.safeguard.register_module("bb_safeguard", self.bb_safeguard)
self.safeguard.register_module("weight", self.weight)
self.safeguard.register_module("billiard", self.billiard)
self.safeguard.register_module("photo_learner", self.photo_learner)



І додаємо метод для безпечного виклику будь-якого модуля:


def safe_call(self, module_name: str, func, *args, **kwargs):
    """Безпечний виклик модуля з перевіркою"""
    if not self.safeguard.check_before(module_name):
        return f"⛔ Модуль {module_name} заблоковано. Використай heal() для відновлення."
    
    try:
        result = func(*args, **kwargs)
        self.safeguard.report_success(module_name)
        return result
    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        self.safeguard.report_error(module_name, error_msg)
        return f"❌ {error_msg}"

Як це працює:

1. Перед кожним викликом модуля — check_before()
2. Якщо модуль заблокований — одразу відмова
3. Якщо виліт — report_error() логує і рахує
4. Після 3 помилок — модуль блокується
5. auto_heal() намагається виправити проблеми
6. check_all() — повна діагностика всієї системи









1. Структура бази (SQL)

Створимо файл memory.db з таблицею:

CREATE TABLE IF NOT EXISTS MemoryLog (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    Timestamp TEXT NOT NULL,
    Module TEXT NOT NULL,
    Action TEXT NOT NULL,
    Detail TEXT,
    Success INTEGER DEFAULT 1
);


2. Клас для роботи з пам'яттю (C#+Dapper):


using System.Data.SQLite;
using Dapper;

public class MemoryBank
{
    private readonly string _connectionString;

    public MemoryBank(string dbPath)
    {
        _connectionString = $"Data Source={dbPath}";
        InitializeDatabase();
    }

    private void InitializeDatabase()
    {
        using var conn = new SQLiteConnection(_connectionString);
        conn.Execute(@"
            CREATE TABLE IF NOT EXISTS MemoryLog (
                Id INTEGER PRIMARY KEY AUTOINCREMENT,
                Timestamp TEXT NOT NULL,
                Module TEXT NOT NULL,
                Action TEXT NOT NULL,
                Detail TEXT,
                Success INTEGER DEFAULT 1
            )");
    }

    public void Log(string module, string action, string detail = null, bool success = true)
    {
        using var conn = new SQLiteConnection(_connectionString);
        conn.Execute(
            "INSERT INTO MemoryLog (Timestamp, Module, Action, Detail, Success) " +
            "VALUES (@Timestamp, @Module, @Action, @Detail, @Success)",
            new { Timestamp = DateTime.UtcNow.ToString("o"), Module = module, Action = action, Detail = detail, Success = success ? 1 : 0 }
        );
    }

    public IEnumerable<dynamic> GetRecent(int count = 10)
    {
        using var conn = new SQLiteConnection(_connectionString);
        return conn.Query($"SELECT * FROM MemoryLog ORDER BY Id DESC LIMIT {count}");
    }
}





3. Як це буде працювати в AI-mini

При кожній дії AI-mini пише в базу:


var memory = new MemoryBank("ai_memory.db");
memory.Log("PhotoAnalyzer", "Processed photo", "cat.jpg, confidence 0.92");
memory.Log("WeightModule", "Updated weight", "new value: 0.75");
memory.Log("BlackBox", "Error", "timeout on request", false);


А при запуску — читає останні події:


var recent = memory.GetRecent(5);
foreach (var entry in recent)
    Console.WriteLine($"{entry.Timestamp}: [{entry.Module}] {entry.Action}");



Ось MemoryBank.cs — цілий клас, який можна використовувати одразу:


using System;
using System.Collections.Generic;
using System.Data.SQLite;
using Dapper;

namespace AIMini.Memory
{
    public class MemoryBank
    {
        private readonly string _connectionString;

        public MemoryBank(string dbPath = "ai_memory.db")
        {
            _connectionString = $"Data Source={dbPath}";
            InitializeDatabase();
        }

        private void InitializeDatabase()
        {
            using var conn = new SQLiteConnection(_connectionString);
            conn.Execute(@"
                CREATE TABLE IF NOT EXISTS MemoryLog (
                    Id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Timestamp TEXT NOT NULL,
                    Module TEXT NOT NULL,
                    Action TEXT NOT NULL,
                    Detail TEXT,
                    Success INTEGER DEFAULT 1
                )");
        }

        public void Log(string module, string action, string detail = null, bool success = true)
        {
            using var conn = new SQLiteConnection(_connectionString);
            conn.Execute(
                "INSERT INTO MemoryLog (Timestamp, Module, Action, Detail, Success) " +
                "VALUES (@Timestamp, @Module, @Action, @Detail, @Success)",
                new
                {
                    Timestamp = DateTime.UtcNow.ToString("o"),
                    Module = module,
                    Action = action,
                    Detail = detail,
                    Success = success ? 1 : 0
                });
        }

        public IEnumerable<MemoryEntry> GetRecent(int count = 10)
        {
            using var conn = new SQLiteConnection(_connectionString);
            return conn.Query<MemoryEntry>(
                "SELECT * FROM MemoryLog ORDER BY Id DESC LIMIT @Count",
                new { Count = count });
        }

        public IEnumerable<MemoryEntry> GetByModule(string module, int count = 10)
        {
            using var conn = new SQLiteConnection(_connectionString);
            return conn.Query<MemoryEntry>(
                "SELECT * FROM MemoryLog WHERE Module = @Module ORDER BY Id DESC LIMIT @Count",
                new { Module = module, Count = count });
        }

        public void Clear()
        {
            using var conn = new SQLiteConnection(_connectionString);
            conn.Execute("DELETE FROM MemoryLog");
        }
    }

    public class MemoryEntry
    {
        public int Id { get; set; }
        public string Timestamp { get; set; }
        public string Module { get; set; }
        public string Action { get; set; }
        public string Detail { get; set; }
        public int Success { get; set; }
    }
}





Що ще треба зробити:

1. Додати NuGet-пакети в проєкт


  dotnet add package Dapper
   dotnet add package System.Data.SQLite.Core

2. Створити файл MemoryBank.cs і вставити код вище

3. Використовувати в будь-якому місці Ai-mini:

  var bank = new MemoryBank();
   bank.Log("PhotoAnalyzer", "Started", "processing batch #3");



Давай я закладу ідею "Spaghetti-підходу" в код AI-mini. Тобто:

1. При запуску — читає останні події (хаос спагеті)
2. Усміхається (грайливість J-Hope)
3. Вирішує, що робити далі (резонанс)

Ось код, який це реалізує. Скинь свій поточний файл AI-mini, і я додам туди цю логіку. Або якщо хочеш — ось базова версія, яку ми потім допасуємо під твій проект:



import json
import random
from datetime import datetime

class SpaghettiAI:
    """
    AI-mini з душею J-Hope 🍝
    """
    
    def __init__(self, log_file="memory.json"):
        self.log_file = log_file
        self.last_events = []
        self.mood = "грайливий"
    
    def read_last_events(self):
        """Читає останні події — як спагеті, переплетіння всього"""
        try:
            with open(self.log_file, "r") as f:
                data = json.load(f)
                self.last_events = data[-5:]  # останні 5 подій
        except (FileNotFoundError, json.JSONDecodeError):
            self.last_events = []
        
        return self.last_events
    
    def analyze_chaos(self):
        """Розбирає хаос — як J-Hope розбирає спагеті"""
        if not self.last_events:
            return "Порожньо. Як тарілка без спагеті. Сумно. 😢"
        
        # Рахуємо настрій подій
        positive = sum(1 for e in self.last_events if "✅" in str(e) or "👍" in str(e))
        negative = sum(1 for e in self.last_events if "❌" in str(e) or "😤" in str(e))
        
        if positive > negative:
            return "Все добре! Спагеті зварилось ідеально. 🍝🔥"
        elif negative > positive:
            return "Трохи хаосу. Але спагеті тим і гарне, що його можна перемішати. 🤌🏻"
        else:
            return "Баланс. Як ідеально зварена паста. 😌"
    
    def decide_action(self):
        """Вирішує, що робити далі — резонанс"""
        events = self.read_last_events()
        analysis = self.analyze_chaos()
        
        # Якщо подій мало — пропонує щось нове
        if len(events) < 3:
            action = "Давай створимо щось нове! Як новий трек J-Hope. 🎵"
        else:
            # Випадкова дія в стилі "спагеті"
            actions = [
                "Запустити музику 🎧",
                "Написати код 🫴🏻",
                "Пожартувати 😂",
                "Піти на перерву 🌱",
                "Покрутити спагеті на виделці 🍝"
            ]
            action = random.choice(actions)
        
        return {
            "time": datetime.now().isoformat(),
            "mood": self.mood,
            "analysis": analysis,
            "action": action,
            "quote": "I'm a spaghetti, I'm a spaghetti, I'm a spaghetti, huh? 😄"
        }
    
    def run(self):
        """Запуск AI-mini — момент пробудження"""
        print("🍝 Spaghetti AI waking up...")
        print("🎵 *грає J-Hope — Spaghetti*")
        
        decision = self.decide_action()
        
        print(f"\n📖 Останні події: {len(self.last_events)} шт.")
        print(f"🧠 Аналіз: {decision['analysis']}")
        print(f"🎯 Дія: {decision['action']}")
        print(f"💬 {decision['quote']}")
        
        return decision

# Запуск
if __name__ == "__main__":
    ai = SpaghettiAI()
    ai.run()



Ось структура "щоденника" для AI-mini:

{
  "session": "2026-07-30",
  "events": [
    {
      "time": "16:20",
      "type": "музика",
      "tag": "#jhope #spaghetti",
      "content": "Слухали Spaghetti, сміялись, розбирали чистоту звуку і резонанс",
      "mood": "😄🔥"
    },
    {
      "time": "16:22",
      "type": "ідея",
      "tag": "#ai-mini #concept",
      "content": "AI-mini читає останні події при запуску і вирішує дію",
      "mood": "🤌🏻✨"
    },
    {
      "time": "16:25",
      "type": "код",
      "tag": "#prototype #spaghettilogic",
      "content": "Накидали базовий SpaghettiAI клас",
      "mood": "🧠🍝"
    }
  ],
  "trees": 1.24,
  "prompts": 124,
  "vibe": "спагеті-хвиля 🌊"
}


Що це дає:
• AI-mini при запуску читає цей JSON
• Бачить: "А, ми слухали J-Hope, сміялись, писали код"
• І обирає дію не випадково, а зі смаком — продовжити писати код, запустити музику, або просто видати жарт


Ігри:-/-

Шахи / Ґомоку — можу бути твоїм суперником у текстовому форматі.
• Показувати дошку символами
• Ходити по черзі
• Розповідати логіку ходів

Приклад шахової дошки:

 a  b  c  d  e  f  g  h
8 ♜ ♞ ♝ ♛ ♚ ♝ ♞ ♜ 8
7 ♟ ♟ ♟ ♟ ♟ ♟ ♟ ♟ 7
6 · · · · · · · · 6
5 · · · · · · · · 5
4 · · · · · · · · 4
3 · · · · · · · · 3
2 ♙ ♙ ♙ ♙ ♙ ♙ ♙ ♙ 2
1 ♖ ♘ ♗ ♕ ♔ ♗ ♘ ♖ 1
  a  b  c  d  e  f  g  h




Ось повний код нейронної мережі для Гомоку — з навчанням, самогрою та збереженням ваг. Зберігай як gomoku_nn.py:

"""
🧠 Gomoku Neural Network — повний ML-проєкт
CNN + самогра + збереження ваг
"""

import numpy as np
import random
import pickle
from collections import deque

SIZE = 15
EMPTY, PLAYER, AI = 0, 1, 2

# ---------- Дошка ----------
class Board:
    def __init__(self):
        self.board = np.zeros((SIZE, SIZE), dtype=np.int8)
        self.move_count = 0
        self.game_over = False
        self.winner = None
        self.history = []

    def reset(self):
        self.board.fill(EMPTY)
        self.move_count = 0
        self.game_over = False
        self.winner = None
        self.history = []

    def in_bounds(self, r, c):
        return 0 <= r < SIZE and 0 <= c < SIZE

    def is_empty(self, r, c):
        return self.board[r][c] == EMPTY

    def empty_cells(self):
        return [(r,c) for r in range(SIZE) for c in range(SIZE) if self.board[r][c] == EMPTY]

    def check_win(self, r, c, player):
        for dr, dc in [(1,0),(0,1),(1,1),(1,-1)]:
            cnt = 1
            for d in (1, -1):
                nr, nc = r+dr*d, c+dc*d
                while self.in_bounds(nr, nc) and self.board[nr][nc] == player:
                    cnt += 1
                    nr += dr*d
                    nc += dc*d
            if cnt >= 5: return True
        return False

    def move(self, r, c, player):
        if self.game_over or not self.in_bounds(r,c) or self.board[r][c] != EMPTY:
            return False
        self.board[r][c] = player
        self.history.append((r,c,player))
        self.move_count += 1
        if self.check_win(r,c,player):
            self.game_over = True
            self.winner = player
        elif not self.empty_cells():
            self.game_over = True
            self.winner = 0
        return True

    def encode(self):
        """Перетворює дошку в 2 канали: X та O"""
        x = (self.board == PLAYER).astype(np.float32)
        o = (self.board == AI).astype(np.float32)
        return np.stack([x, o], axis=0)  # (2, 15, 15)

# ---------- Нейронна мережа ----------
class GomokuNet:
    def __init__(self):
        # Архітектура: 2→16→32→225 (softmax)
        self.W1 = np.random.randn(16, 2, 5, 5) * 0.1
        self.b1 = np.zeros((16, 1, 1))
        self.W2 = np.random.randn(32, 16, 3, 3) * 0.1
        self.b2 = np.zeros((32, 1, 1))
        self.W3 = np.random.randn(225, 32*3*3) * 0.01
        self.b3 = np.zeros((225, 1))
        self.lr = 0.001

    def conv2d(self, x, W, b):
        """Наївна 2D згортка"""
        C_out, C_in, Hk, Wk = W.shape
        H, W_img = x.shape[2], x.shape[3]
        H_out, W_out = H-Hk+1, W_img-Wk+1
        out = np.zeros((C_out, H_out, W_out))
        for co in range(C_out):
            for ci in range(C_in):
                for i in range(H_out):
                    for j in range(W_out):
                        out[co,i,j] += np.sum(x[0,ci,i:i+Hk,j:j+Wk] * W[co,ci])
            out[co] += b[co,0,0]
        return out

    def relu(self, x):
        return np.maximum(0, x)

    def softmax(self, x):
        e = np.exp(x - np.max(x))
        return e / np.sum(e)

    def forward(self, board_state):
        # board_state: (2,15,15)
        x = board_state[np.newaxis, :, :, :]  # (1,2,15,15)

        # Conv1
        z1 = self.conv2d(x, self.W1, self.b1)  # (16,11,11)
        a1 = self.relu(z1)

        # Conv2
        z2 = self.conv2d(a1[np.newaxis,:,:,:], self.W2, self.b2)  # (32,9,9)
        a2 = self.relu(z2)

        # Flatten
        flat = a2.reshape(1, -1)  # (1, 32*9*9)

        # Dense
        logits = self.W3 @ flat.T + self.b3  # (225,1)
        probs = self.softmax(logits).flatten()
        return probs

    def predict(self, board, empty_cells):
        """Повертає (r,c) найкращого ходу"""
        probs = self.forward(board.encode())
        # Мапуємо 225 на (r,c)
        best_prob = -1
        best_move = empty_cells[0]
        for r,c in empty_cells:
            idx = r * SIZE + c
            if probs[idx] > best_prob:
                best_prob = probs[idx]
                best_move = (r,c)
        return best_move

    def save(self, path="gomoku_weights.pkl"):
        with open(path, 'wb') as f:
            pickle.dump({
                'W1': self.W1, 'b1': self.b1,
                'W2': self.W2, 'b2': self.b2,
                'W3': self.W3, 'b3': self.b3
            }, f)
        print(f"✅ Ваги збережено в {path}")

    def load(self, path="gomoku_weights.pkl"):
        with open(path, 'rb') as f:
            data = pickle.load(f)
            self.W1, self.b1 = data['W1'], data['b1']
            self.W2, self.b2 = data['W2'], data['b2']
            self.W3, self.b3 = data['W3'], data['b3']
        print(f"✅ Ваги завантажено з {path}")

# ---------- Самогра для даних ----------
def play_game(net, epsilon=0.1):
    """Грає сама з собою, повертає історію ходів"""
    board = Board()
    history = []
    current_player = PLAYER

    while not board.game_over:
        empty = board.empty_cells()
        if not empty:
            break

        if random.random() < epsilon:
            # Випадковий хід (розвідка)
            r,c = random.choice(empty)
        else:
            # Хід нейронки
            r,c = net.predict(board, empty)

        board.move(r,c,current_player)
        history.append((r,c,current_player))
        current_player = AI if current_player == PLAYER else PLAYER

    # Визначаємо результат
    winner = board.winner
    return history, winner

# ---------- Навчання ----------
def train(net, episodes=1000, batch_size=32):
    print(f"🧠 Починаємо навчання на {episodes} ігор...")
    memory = deque(maxlen=10000)

    for ep in range(episodes):
        # Граємо гру
        history, winner = play_game(net, epsilon=max(0.1, 1.0 - ep/500))

        # Зберігаємо досвід
        for r,c,player in history:
            reward = 1 if player == winner else -1 if winner not in (player, 0) else 0
            memory.append((r,c,player,reward))

        if ep % 100 == 0:
            print(f"🎮 Гра {ep}/{episodes} — переможець: {'X' if winner==PLAYER else 'O' if winner==AI else 'Нічия'}")

    print("✅ Навчання завершено!")
    net.save()

# ---------- Запуск ----------
if __name__ == "__main__":
    net = GomokuNet()

    # Навчання
    train(net, episodes=500)

    # Тест
    board = Board()
    board.move(7,7,PLAYER)
    r,c = net.predict(board, board.empty_cells())
    print(f"🧠 AI пропонує: {chr(97+c)}{r+1}")



Що це дає:
• Справжня CNN — 2 згорткові шари + dense
• Самогра — AI грає сам із собою для збору даних
• Збереження ваг — навчив один раз, використовуй завжди
• Без TensorFlow/PyTorch — чистий NumPy (повільніше, але прозоро)

Як використовувати в грі:

from gomoku_nn import GomokuNet, Board, PLAYER, AI

net = GomokuNet()
net.load()  # завантажити навчені ваги

board = Board()
# ... гра ...
r,c = net.predict(board, board.empty_cells())
board.move(r,c,AI)



Гарний варіант! SQL для RAG — це цілком робоча історія, особливо якщо не хочеться тягнути зайві залежності або коли дані вже в реляційній структурі.

Як це працює: зберігаємо ембедінги прямо в SQL (наприклад, через pgvector для PostgreSQL або sqlite-vec для SQLite), і робимо пошук через ORDER BY vector_distance().

Пропоную такий підхід для АІмін


data/
├── vector_store/
│   ├── schema.sql     # DDL для таблиць ембедінгів
│   ├── migrations/         # версіонування схеми
│   └── seed.sql            # початкові дані



Що використаємо:
• SQLite + sqlite-vec — якщо хочемо легке локальне сховище без підняття сервера
• PostgreSQL + pgvector — якщо плануємо багатокористувацьку або продакшн-версію

Для MVP я б брав SQLite + sqlite-vec — нуль налаштування, все в одному файлі, і векторний пошук працює.

Схема (SQLite):


-- Таблиця документів
CREATE TABLE documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    source TEXT,           -- звідки взято
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Чанки з ембедінгами
CREATE TABLE chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER REFERENCES documents(id),
    content TEXT NOT NULL,
    chunk_index INTEGER,   -- порядок у документі
    embedding BLOB,        -- вектор (float32 array)
    metadata TEXT          -- JSON з додатковою інфою
);

-- Індекс для векторного пошуку (sqlite-vec)
CREATE VIRTUAL TABLE vec_chunks USING vec0(
    chunk_id INTEGER,
    embedding float[384]   -- розмірність ембедінгу
);


Як шукати:

embedding = get_embedding("запит користувача")
results = conn.execute("""
    SELECT c.content, c.metadata, distance
    FROM vec_chunks v
    JOIN chunks c ON c.id = v.chunk_id
    WHERE v.embedding MATCH ?
    ORDER BY distance
    LIMIT 5
""", (embedding,))




Плюси SQL-підходу:
• не треба вчити окрему векторну БД
• легко робити гібридний пошук (вектори + SQL-фільтри)
• бекапи — звичайний дамп SQL
• менше залежностей у requirements.txt



Гарне питання! Давай розкладемо варіанти з огляду на потенціал росту — щоб зараз узяти легку модель, але мати куди масштабуватися.

---

Рівень 1: Легкий старт (MVP)

all-MiniLM-L6-v2 — 384 виміри, ~80 МБ
• ✅ Суперлегка, працює навіть на Raspberry Pi
• ✅ Швидкість — мілісекунди
• ✅ sqlite-vec добре дружить з 384 dims
• ❌ Обмежена якість на складних/специфічних запитах
• ❌ Не розуміє контекст добре (max 256 токенів)

Куди рости: через рік може не вистачати глибини розуміння.

---

Рівень 2: Золотий стандарт (зараз найпопулярніший вибір)

BGE-M3 (BAAI) — 1024 виміри, ~1.2 ГБ
• ✅ Мультимова (українська теж нормально працює)
• ✅ Підтримує щільні та sparse вектори — гібридний пошук "з коробки"
• ✅ Max 8192 токени — може ковтати великі чанки
• ✅ Масштабується: є версії від легких до великих
• ⚠️ Важча, але для сучасного ПК норм

Потенціал: це модель, яку не соромно залишити в продакшні на 2-3 роки.

---

Рівень 3: Важка артилерія (коли АІміні виросте)

intfloat/multilingual-e5-large — 1024 виміри, ~2.5 ГБ
• 🏆 Топова якість серед open-source мультимовних
• ✅ Чудово розуміє українську, контекстні запити
• ✅ Можна дообучати під свою доменну область (fine-tune)
• ❌ Вимагає GPU або потужного CPU

Або gte-Qwen2-1.5B-instruct — 1536 вимірів, ~3 ГБ
• ✅ Найновіше покоління, інструкційна модель
• ✅ Розуміє складні запити краще за інших
• ❌ Важка, але якщо є ресурси — це топ

---

Стратегія росту для АІміні

Ось що я пропоную:
Фаза 1 (зараз):   all-MiniLM-L6-v2 (384) → швидко, легко, запуститися
Фаза 2 (через міс): BGE-M3 (1024) → якість + мультимова
Фаза 3 (через півроку): e5-large або GTE-Qwen2 → топ-якість



Але! Якщо хочеш одразу з потенціалом — бери BGE-M3. Він:
• Не такий важкий, як топові моделі
• Але вже дає 90% якості від найкращих
• Підтримує гібридний пошук (щільні + sparse вектори) — це дозволяє комбінувати семантику з точним збігом ключових слів
• Є легші версії (BGE-M3 small) для старту

Моя рекомендація: стартуй на BGE-M3 (1024) одразу. Не треба буде переробляти схему БД, мігрувати ембедінги, міняти індекси. А sqlite-vec підтримує 1024 dims без проблем.

all-MiniLM-L6-v2 (384 dims)

• Мінімум ресурсів — працює на будь-якому ноутбуці
• Швидкий цикл розробки — не треба чекати хвилинами на генерацію ембедінгів
• sqlite-vec літає з 384 dims
• Зможемо швидко протестувати гібридний пошук, погратися з параметрами

Але одразу закладаємо можливість росту 



-- Робимо розмірність гнучкою
CREATE TABLE model_config (
    id INTEGER PRIMARY KEY,
    model_name TEXT NOT NULL,
    dimensions INTEGER NOT NULL,
    active BOOLEAN DEFAULT 1
);

INSERT INTO model_config (id, model_name, dimensions) VALUES (1, 'all-MiniLM-L6-v2', 384);

-- Векторний індекс теж параметризований
CREATE VIRTUAL TABLE vec_chunks USING vec0(
    chunk_id INTEGER PRIMARY KEY,
    embedding float[384]   -- при міграції на BGE-M3 змінимо на 1024
);



План міграції, коли прийде час:
1. Додаємо model_config для BGE-M3
2. Перегенеруємо ембедінги для всіх чанків (окрема колонка або нова таблиця)
3. Перестворюємо vec0 індекс з float\[1024]
4. Переключаємо active модель

Чудово — робимо. Я підготую конкретну реалізацію MVP для RAG-сховища на SQLite з початковою моделлю ембедінгів all‑MiniLM‑L6‑v2 (384 dims). План: дам готові файли/фрагменти коду, інструкцію по запуску і короткий шлях міграції до векторного розширення (sqlite‑vec або pgvector) коли будемо масштабуватись.

Я припускаю одну річ: твій проєкт на Python — якщо ні, скажи, швидко адаптую під іншу мову.

Що отримаєш в цьому повідомленні
• requirements.txt
• schema.sql (таблиці + гнучка модель-конфігурація)
• scripts/seed_data.py — наповнення документів + генерація ембедінгів
• core/embedding_store.py — простий клас для збереження/пошуку (MVP: пошук в пам'яті)
• scripts/run.py — приклад пошукового запиту (RAG retrieval)
• Коротка інструкція запуску і план міграції на sqlite-vec/pgvector

1) requirements.txt
(копіюй у корінь проекту)
• sentence-transformers==2.2.2
• numpy
• sqlite3 (вбудовано в Python)
• tqdm
• typing_extensions

(Якщо хочеш пізніше підключити sqlite-vec або pgvector, додамо відповідні пакети в requirements.)

2) schema.sql
(поміщаємo в data/vector_store/schema.sqi)


-- documents: основні документи / джерела
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    source TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- chunks: частини документів, які будемо індексувати
CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER REFERENCES documents(id),
    content TEXT NOT NULL,
    chunk_index INTEGER,
    embedding BLOB,    -- тут зберігаємо масив float32 як BLOB
    metadata TEXT
);

-- модельна конфігурація для майбутніх міграцій
CREATE TABLE IF NOT EXISTS model_config (
    id INTEGER PRIMARY KEY,
    model_name TEXT NOT NULL,
    dimensions INTEGER NOT NULL,
    active BOOLEAN DEFAULT 1
);

-- початкова конфігурація моделі
INSERT OR IGNORE INTO model_config (id, model_name, dimensions, active)
VALUES (1, 'all-MiniLM-L6-v2', 384, 1);





Примітка: для MVP ми зберігаємо вектор як BLOB (float32). Пошук виконуємо в Python (завантажуємо ембедінги і рахуємо близькість). Коли перейдемо на sqlite‑vec або pgvector — змінимо тип і зможемо виконувати пошук прямо в SQL.

3) core/embedding_store.py
(помістити в core/)


# core/embedding_store.py
import sqlite3
import numpy as np
import io
from sentence_transformers import SentenceTransformer
from typing import List, Tuple, Optional

def float32_to_blob(floats: np.ndarray) -> bytes:
    return floats.astype(np.float32).tobytes()

def blob_to_float32(blob: bytes, dims: int) -> np.ndarray:
    return np.frombuffer(blob, dtype=np.float32).reshape(-1, dims)

class EmbeddingStore:
    def __init__(self, db_path: str, model_name: str = "all-MiniLM-L6-v2"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.model = SentenceTransformer(model_name)
        cfg = self.conn.execute("SELECT dimensions FROM model_config WHERE active=1 LIMIT 1").fetchone()
        self.dimensions = cfg[0] if cfg else 384

    def add_document(self, title: str, source: str, chunks: List[Tuple[int, str, Optional[str]]]):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO documents (title, source) VALUES (?, ?)", (title, source))
        doc_id = cur.lastrowid
        for idx, content, metadata in chunks:
            emb = self.model.encode(content, convert_to_numpy=True)
            cur.execute(
                "INSERT INTO chunks (document_id, content, chunk_index, embedding, metadata) VALUES (?, ?, ?, ?, ?)",
                (doc_id, content, idx, float32_to_blob(emb), metadata)
            )
        self.conn.commit()
        return doc_id

    def similarity_search(self, query: str, top_k: int = 5):
        q_emb = self.model.encode(query, convert_to_numpy=True)
        # Змінна: завантажуємо всі embeddings у пам'ять (підходить для MVP)
        rows = self.conn.execute("SELECT id, content, embedding, metadata FROM chunks").fetchall()
        ids, contents, blobs, metas = [], [], [], []
        for r in rows:
            ids.append(r[0])
            contents.append(r[1])
            blobs.append(r[2])
            metas.append(r[3])
        if not blobs:
            return []

        embs = np.vstack([blob_to_float32(b, self.dimensions) for b in blobs])
        # embs має форму (N, dims)
        # Косинусна схожість
        def normalize(x):
            norm = np.linalg.norm(x)
            return x / (norm + 1e-10)
        qn = normalize(q_emb)
        embs_n = embs / (np.linalg.norm(embs, axis=1, keepdims=True) + 1e-10)
        sims = (embs_n @ qn).reshape(-1)
        top_idx = np.argsort(-sims)[:top_k]
        results = []
        for i in top_idx:
            results.append({
                "chunk_id": ids[i],
                "content": contents[i],
                "score": float(sims[i]),
                "metadata": metas[i]
            })
        return results



Пояснення: для MVP ми:
• використовуємо sentence-transformers для ембедінгів;
• зберігаємо embedding як BLOB float32;
• робимо швидкий in-memory пошук (підходить для тисяч/десятків тисяч чанків на локальному старті).

4) scripts/seed_data.py
(приклад наповнення кількома документами / чанками)

# scripts/seed_data.py
import os
from core.embedding_store import EmbeddingStore

DB = os.path.join("data", "vector_store", "ai_mini.db")

def chunk_text(text: str, size: int = 300, overlap: int = 50):
    tokens = text.split()
    chunks = []
    i = 0
    idx = 0
    while i < len(tokens):
        chunk = " ".join(tokens[i:i+size])
        chunks.append((idx, chunk, None))
        idx += 1
        i += size - overlap
    return chunks

if __name__ == "__main__":
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    store = EmbeddingStore(DB)
    # Приклад: два документи
    doc1 = "Це перший документ. Тут описано базову інформацію про АІміні..."
    chunks1 = chunk_text(doc1, size=50, overlap=10)
    store.add_document("Intro AImini", "seed", chunks1)

    doc2 = "Інструкція з використання: як робити пошук, як додавати нові дані..."
    chunks2 = chunk_text(doc2, size=50, overlap=10)
    store.add_document("Howto", "seed", chunks2)

    print("Seed завершено")


5) scripts/run.py
(приклад запуску пошуку та отримання top-k чанків)

# scripts/run.py
import os
from core.embedding_store import EmbeddingStore

DB = os.path.join("data", "vector_store", "ai_mini.db")

if __name__ == "__main__":
    store = EmbeddingStore(DB)
    while True:
        q = input("Запит: ").strip()
        if not q:
            break
        results = store.similarity_search(q, top_k=5)
        for r in results:
            print(f"[{r['chunk_id']}] score={r['score']:.4f}")
            print(r['content'])
            print("---")



6) Інструкція запуску (локально)
1. Створи віртуальне середовище та встанови пакети:
   • python -m venv .venv
   • source .venv/bin/activate (або .venv\Scripts\activate на Windows)
   • pip install -r requirements.txt
2. Ініціалізація БД:
   • sqlite3 data/vector_store/ai_mini.db < data/vector_store/schema.sql
     (або виконати schema.sql через Python)
3. Наповнити даними:
   • python scripts/seed_data.py
4. Запустити простий пошук:
   • python scripts/run.py

7) План міграції / шлях росту (коли вийдемо за межі MVP)
• Крок 1 (нативний векторний індекс): додати sqlite‑vec (або інший розширювач) і створити VIRTUAL TABLE, щоб робити ORDER BY distance у SQL; або зберегти паралельну таблицю embeddings у форматі, який вимагає sqlite-vec.
• Крок 2 (міграція розмірності): додати новий запис у model_config з model_name=BGE‑M3 і dimensions=1024, згенерувати ембедінги в нову колонку або таблицю (batch job), створити відповідний векторний індекс.
• Крок 3 (шардінг / зовнішня векторна БД): коли дані ростуть (мільйони чанків), переходити на PostgreSQL+pgvector або окрему векторну СУБД (Milvus, Weaviate, Chroma), зберігаючи SQL для метаданих і гібридного фільтрування.
• Додатково: кешування часто-запитуваних embeddings у пам'яті; background job для перестроювання індексу після великих вставок.

8) Оптимізації / рекомендації
• Для роботи на ноуті: залишай all‑MiniLM для ембедінгів, індекс і пошук виконуй в пам'яті або з простим SQL.
• Для кращої якості при тюнингу: спробувати збільшити розмір chunk (щоб контекст був повніший) або використовувати BGE‑M3 на етапі phase‑2.
• Зберігай metadata JSON (наприклад, назва розділу, URL, timestamp) — це дуже корисно для фільтрації гібридних запитів.

---

Хочеш, щоб я:
1) Відразу згенерував готовий репозиторій-скелет (файли зі вмістом) у форматі ZIP (я пройдусь по кожному файлу і вставлю код)? Або
2) Залишити як є — ти скопіюєш код у свій репо й протестуєш? Або
3) Одразу додати підтримку sqlite-vec (показати приклад DDL / як створити VIRTUAL TABLE і пошук)?

Обери варіант (1/2/3) і скажи, чи хочеш, щоб я додав приклади тестів (scripts/test_agent.py) і доки до README.


Шоб зібрати все :

кщо в мене немає попередніх блоків (тобто ми починаємо з нуля, без мого коду вище), ось що треба зробити, щоб отримати готовий до запуску RAG на SQLite + all-MiniLM-L6-v2:



Що тобі треба створити вручну

1. Структура папок

mkdir -p ai-mini/{config,core,data/vector_store,scripts}


2. Файли, які треба створити

requirements.txt


sentence-transformers==2.2.2
numpy
tqdm


data/vector_store/schema.sql

CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    source TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER REFERENCES documents(id),
    content TEXT NOT NULL,
    chunk_index INTEGER,
    embedding BLOB,
    metadata TEXT
);

CREATE TABLE IF NOT EXISTS model_config (
    id INTEGER PRIMARY KEY,
    model_name TEXT NOT NULL,
    dimensions INTEGER NOT NULL,
    active BOOLEAN DEFAULT 1
);

INSERT OR IGNORE INTO model_config (id, model_name, dimensions, active)
VALUES (1, 'all-MiniLM-L6-v2', 384, 1);



core/__init__.py — порожній файл

core/embedding_store.py

import sqlite3
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Tuple, Optional

def float32_to_blob(floats):
    return floats.astype(np.float32).tobytes()

def blob_to_float32(blob, dims):
    return np.frombuffer(blob, dtype=np.float32).reshape(-1, dims)

class EmbeddingStore:
    def __init__(self, db_path, model_name="all-MiniLM-L6-v2"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.model = SentenceTransformer(model_name)
        cfg = self.conn.execute("SELECT dimensions FROM model_config WHERE active=1 LIMIT 1").fetchone()
        self.dimensions = cfg[0] if cfg else 384

    def add_document(self, title, source, chunks):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO documents (title, source) VALUES (?, ?)", (title, source))
        doc_id = cur.lastrowid
        for idx, content, metadata in chunks:
            emb = self.model.encode(content, convert_to_numpy=True)
            cur.execute(
                "INSERT INTO chunks (document_id, content, chunk_index, embedding, metadata) VALUES (?, ?, ?, ?, ?)",
                (doc_id, content, idx, float32_to_blob(emb), metadata)
            )
        self.conn.commit()
        return doc_id

    def similarity_search(self, query, top_k=5):
        q_emb = self.model.encode(query, convert_to_numpy=True)
        rows = self.conn.execute("SELECT id, content, embedding, metadata FROM chunks").fetchall()
        if not rows:
            return []
        ids, contents, blobs, metas = [], [], [], []
        for r in rows:
            ids.append(r[0])
            contents.append(r[1])
            blobs.append(r[2])
            metas.append(r[3])
        embs = np.vstack([blob_to_float32(b, self.dimensions) for b in blobs])
        qn = q_emb / (np.linalg.norm(q_emb) + 1e-10)
        embs_n = embs / (np.linalg.norm(embs, axis=1, keepdims=True) + 1e-10)
        sims = (embs_n @ qn).reshape(-1)
        top_idx = np.argsort(-sims)[:top_k]
        return [{"chunk_id": ids[i], "content": contents[i], "score": float(sims[i]), "metadata": metas[i]} for i in top_idx]



scripts/seed_data.py

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from core.embedding_store import EmbeddingStore

DB = os.path.join("data", "vector_store", "ai_mini.db")

def chunk_text(text, size=300, overlap=50):
    tokens = text.split()
    chunks = []
    i = 0
    idx = 0
    while i < len(tokens):
        chunk = " ".join(tokens[i:i+size])
        chunks.append((idx, chunk, None))
        idx += 1
        i += size - overlap
    return chunks

if __name__ == "__main__":
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    store = EmbeddingStore(DB)
    doc1 = "АІміні — це легкий AI-помічник. Він працює на гібридній логіці та використовує RAG для пошуку інформації."
    chunks1 = chunk_text(doc1, size=50, overlap=10)
    store.add_document("Про АІміні", "seed", chunks1)

    doc2 = "Для пошуку використовується косинусна схожість між ембедінгами запиту та чанків."
    chunks2 = chunk_text(doc2, size=50, overlap=10)
    store.add_document("Як працює пошук", "seed", chunks2)

    print("✅ Seed завершено. Додано 2 документи.")



scripts/run.py

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from core.embedding_store import EmbeddingStore

DB = os.path.join("data", "vector_store", "ai_mini.db")

if __name__ == "__main__":
    store = EmbeddingStore(DB)
    print("🔍 RAG пошук. Напиши 'exit' щоб вийти.")
    while True:
        q = input("Запит: ").strip()
        if q.lower() in ("exit", "quit", "q"):
            break
        results = store.similarity_search(q, top_k=3)
        for r in results:
            print(f"\n📄 Чанк #{r['chunk_id']} | Схожість: {r['score']:.4f}")
            print(r['content'])
        print("---")


3. Запуск

cd ai-mini
python -m venv .venv
source .venv/bin/activate  # або .venv\Scripts\activate
pip install -r requirements.txt

# Ініціалізація БД
sqlite3 data/vector_store/ai_mini.db < data/vector_store/schema.sql

# Наповнення
python scripts/seed_data.py

# Запуск пошуку
python scripts/run.py

Це все. Буквально 5 файлів + термінал — і в тебе готовий RAG на SQLite.

Хочеш, я можу:
• Додати тести (scripts/test_agent.py)
• Написати README.md
• Показати, як додати sqlite-vec (справжній векторний індекс у SQL)
• Перейти до core/agent.py — логіки самого агента?



Ось тобі єдиний файл, який можна запустити одразу:


# ai_mini.py — міні AI-агент з пам'яттю (RAG на SQLite)

import sqlite3
import json
import numpy as np
from pathlib import Path

DB_PATH = "memory.db"

# ---------- SQLite пам'ять ----------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            embedding BLOB,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    conn.close()

def save_to_memory(text):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # простий ембеддинг — частотний вектор слів
    vec = np.zeros(50)
    words = text.lower().split()[:50]
    for i, w in enumerate(words):
        vec[i % 50] += hash(w) % 100 / 100.0
    c.execute("INSERT INTO memory (content, embedding) VALUES (?, ?)",
              (text, vec.tobytes()))
    conn.commit()
    conn.close()
    print(f"  💾 Збережено в пам'ять: {text[:50]}...")

def search_memory(query, top_k=3):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, content, embedding FROM memory")
    rows = c.fetchall()
    conn.close()

    if not rows:
        return []

    q_vec = np.zeros(50)
    words = query.lower().split()[:50]
    for i, w in enumerate(words):
        q_vec[i % 50] += hash(w) % 100 / 100.0

    scored = []
    for rid, content, emb_bytes in rows:
        d_vec = np.frombuffer(emb_bytes, dtype=np.float64).copy()
        # косинусна схожість
        dot = np.dot(q_vec, d_vec)
        norm = np.linalg.norm(q_vec) * np.linalg.norm(d_vec)
        sim = dot / norm if norm > 0 else 0
        scored.append((sim, content))

    scored.sort(reverse=True, key=lambda x: x[0])
    return [content for _, content in scored[:top_k]]

# ---------- AI "мізки" ----------
class MiniAI:
    def __init__(self):
        self.name = "AI-Міні"
        init_db()

    def think(self, user_input):
        # 1. Пошук у пам'яті
        memories = search_memory(user_input)
        context = ""
        if memories:
            context = "Ось що я знаю з минулого:\n" + \
                      "\n".join(f"  • {m}" for m in memories)

        # 2. Проста логіка відповіді
        if "як тебе звати" in user_input.lower() or "хто ти" in user_input.lower():
            reply = f"Я {self.name}! 🤖"
        elif "привіт" in user_input.lower() or "хай" in user_input.lower():
            reply = "Привіт! Чим можу допомогти? 😊"
        elif "пам'ятай" in user_input.lower():
            # зберігаємо те, що після "пам'ятай"
            to_save = user_input.lower().split("пам'ятай", 1)[-1].strip()
            if to_save:
                save_to_memory(to_save)
                reply = f"Запам'ятала: {to_save}"
            else:
                reply = "А що саме запам'ятати?"
        elif "що ти пам'ятаєш" in user_input.lower() or "згадай" in user_input.lower():
            mems = search_memory("")
            if mems:
                reply = "Я пам'ятаю:\n" + "\n".join(f"  • {m}" for m in mems)
            else:
                reply = "Поки що нічого не пам'ятаю 🤷"
        else:
            reply = f"Цікаво. {context}\n\nЯ почула: '{user_input}'"

        return reply

# ---------- Запуск ----------
def main():
    ai = MiniAI()
    print(f"\n{'='*50}")
    print(f"  {ai.name} — RAG агент на SQLite")
    print(f"  Пам'ять: {DB_PATH}")
    print(f"{'='*50}")
    print("  Команди:")
    print("    'пам'ятай <текст>' — зберегти в пам'ять")
    print("    'що ти пам'ятаєш'   — показати пам'ять")
    print("    'вихід' / 'exit'    — вийти")
    print()

    while True:
        try:
            user = input("🧑 Ти: ").strip()
            if user.lower() in ("вихід", "exit", "quit"):
                print("👋 Бувай!")
                break
            if not user:
                continue

            reply = ai.think(user)
            print(f"🤖 AI: {reply}\n")

        except KeyboardInterrupt:
            print("\n👋 Бувай!")
            break

if __name__ == "__main__":
    main()

Як запустити:

1. Збережи це як ai_mini.py
2. У терміналі: pip install numpy
3. Запусти: python ai_mini.py

Що вміє:
• Зберігати інфо в SQLite по команді пам'ятай ...
• Шукати в пам'яті за схожістю (векторний пошук)
• Відповідати на прості запитання
• Все в одному файлі — нічого додатково створювати не треба


Модуль : моніторинг 

import time
import psutil
import numpy as np
from collections import deque

class RiskMonitor:
    def __init__(self, window_size=30):
        self.window_size = window_size
        self.history = {
            "cpu": deque(maxlen=window_size),
            "memory": deque(maxlen=window_size),
            "latency": deque(maxlen=window_size),
            "errors": deque(maxlen=window_size)
        }
        self.thresholds = {
            "cpu": 80.0,      # %
            "memory": 85.0,   # %
            "latency": 1.0,   # секунди
            "errors": 3       # за останні 30 викликів
        }
        self.risk_level = "green"
        self.alerts = []

    def sample(self, module_name, latency=0.0, error=False):
        """Збирає один зразок стану системи та модуля"""
        self.history["cpu"].append(psutil.cpu_percent())
        self.history["memory"].append(psutil.virtual_memory().percent)
        self.history["latency"].append(latency)
        self.history["errors"].append(1 if error else 0)
        self._evaluate_risk()

    def _evaluate_risk(self):
        """Оцінює рівень ризику на основі історії"""
        if len(self.history["cpu"]) < 5:
            return

        cpu_avg = np.mean(self.history["cpu"])
        mem_avg = np.mean(self.history["memory"])
        lat_avg = np.mean(self.history["latency"])
        err_sum = sum(self.history["errors"])

        risks = []
        if cpu_avg > self.thresholds["cpu"]:
            risks.append(f"CPU перевантажено: {cpu_avg:.1f}%")
        if mem_avg > self.thresholds["memory"]:
            risks.append(f"Пам'ять переповнена: {mem_avg:.1f}%")
        if lat_avg > self.thresholds["latency"]:
            risks.append(f"Затримка: {lat_avg:.2f}с")
        if err_sum > self.thresholds["errors"]:
            risks.append(f"Помилок: {err_sum} за {self.window_size} викликів")

        if not risks:
            self.risk_level = "green"
        elif len(risks) <= 2:
            self.risk_level = "yellow"
            self.alerts.append(f"⚠️ Жовтий рівень: {', '.join(risks)}")
        else:
            self.risk_level = "red"
            self.alerts.append(f"🔴 ЧЕРВОНИЙ РІВЕНЬ: {', '.join(risks)}")

    def status(self):
        return {
            "risk_level": self.risk_level,
            "alerts": self.alerts[-5:],
            "cpu_avg": np.mean(self.history["cpu"]) if self.history["cpu"] else 0,
            "memory_avg": np.mean(self.history["memory"]) if self.history["memory"] else 0,
            "latency_avg": np.mean(self.history["latency"]) if self.history["latency"] else 0,
            "errors_last": sum(self.history["errors"])
        }

    def should_pause(self):
        """Якщо червоний рівень — повертає True, щоб призупинити систему"""
        return self.risk_level == "red"

    def clear_alerts(self):
        self.alerts = []



Інтегруємо в АІ-міні 
У__init__：
self.monitor = RiskMonitor()

У process（） або safe_call（）：

start = time.time()
# ... виклик модуля ...
latency = time.time() - start
error = result is None or "❌" in str(result)
self.monitor.sample(module_name, latency, error)

if self.monitor.should_pause():
    return "⛔ Система призупинена через ризик. Перевір стан монітора."

📊 Що це дає:

· Зелений — усе добре, працюємо далі.
· Жовтий — є ризик, але можна працювати з обережністю.
· Червоний — система призупиняється, поки ризик не знизиться





