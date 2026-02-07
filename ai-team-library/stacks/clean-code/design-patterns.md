# Design Patterns

Practical guide to the most useful patterns in modern software development.
Patterns are tools, not goals. Apply them when they solve a real problem, not
to demonstrate knowledge of the Gang of Four catalog.

---

## Defaults

- **When to apply:** You have a recurring design problem and the pattern name
  communicates intent to the team. If you have to explain the pattern every
  code review, it is adding complexity, not clarity.
- **Language:** Patterns shown in pseudocode. Adapt to your language's idioms.
  Many languages have built-in support (e.g., first-class functions replace
  simple Strategy patterns).
- **Scope:** This guide covers the five patterns most frequently useful in
  modern application development. The full GoF catalog has 23; most of the
  remaining 18 are situational.

---

## Strategy

**Problem:** You need to select an algorithm or behavior at runtime without a
chain of `if/else` or `switch` statements.

**Solution:** Define a family of interchangeable behaviors behind a common interface.

```python
# Strategy via functions (simplest form in languages with first-class functions)
def calculate_shipping(weight: float, strategy) -> float:
    return strategy(weight)

def ground_shipping(weight: float) -> float:
    return weight * 1.50

def express_shipping(weight: float) -> float:
    return weight * 3.00 + 10.00

# Usage
cost = calculate_shipping(5.0, express_shipping)
```

```python
# Strategy via classes (when strategies carry state or configuration)
from abc import ABC, abstractmethod

class PricingStrategy(ABC):
    @abstractmethod
    def calculate(self, base_price: float) -> float: ...

class StandardPricing(PricingStrategy):
    def calculate(self, base_price: float) -> float:
        return base_price

class MemberPricing(PricingStrategy):
    def __init__(self, discount_pct: float):
        self.discount_pct = discount_pct

    def calculate(self, base_price: float) -> float:
        return base_price * (1 - self.discount_pct)
```

---

## Factory

**Problem:** Object creation logic is complex, conditional, or should be
decoupled from the calling code.

**Solution:** Centralize creation behind a function or class that returns the
right instance based on input.

```python
# Simple factory function
def create_notifier(channel: str):
    match channel:
        case "email":
            return EmailNotifier()
        case "sms":
            return SmsNotifier()
        case "slack":
            return SlackNotifier()
        case _:
            raise ValueError(f"Unknown channel: {channel}")

# Usage
notifier = create_notifier(user.preferred_channel)
notifier.send(message)
```

**When to use:** When the caller should not know or care about the concrete class.
When creation requires configuration, validation, or conditional logic.

**When to avoid:** When there is only one implementation and no foreseeable need
for polymorphism. A factory for a single class is over-engineering.

---

## Observer

**Problem:** One component needs to notify multiple other components when something
happens, without tight coupling to each listener.

**Solution:** Maintain a list of subscribers. Notify all of them when the event occurs.

```python
class EventBus:
    def __init__(self):
        self._listeners: dict[str, list] = {}

    def subscribe(self, event: str, callback) -> None:
        self._listeners.setdefault(event, []).append(callback)

    def publish(self, event: str, data: dict) -> None:
        for callback in self._listeners.get(event, []):
            callback(data)

# Usage
bus = EventBus()
bus.subscribe("order_placed", lambda d: send_confirmation_email(d))
bus.subscribe("order_placed", lambda d: update_inventory(d))
bus.publish("order_placed", {"order_id": "123", "total": 49.99})
```

**When to use:** Decoupling producers from consumers. Event-driven architectures.
UI event handling.

**When to avoid:** When there is exactly one consumer. A direct function call is
simpler and more traceable than an event bus with one subscriber.

---

## Adapter

**Problem:** You need to use a class or API whose interface does not match what
your code expects.

**Solution:** Wrap the incompatible interface in a class that translates calls
to the expected interface.

```python
# External payment library has an incompatible interface
class LegacyPaymentGateway:
    def make_payment(self, amount_cents: int, cc_number: str) -> bool: ...

# Your code expects this interface
class PaymentProcessor(ABC):
    @abstractmethod
    def charge(self, amount: float, token: str) -> PaymentResult: ...

# Adapter bridges the gap
class LegacyPaymentAdapter(PaymentProcessor):
    def __init__(self, gateway: LegacyPaymentGateway):
        self.gateway = gateway

    def charge(self, amount: float, token: str) -> PaymentResult:
        amount_cents = int(amount * 100)
        success = self.gateway.make_payment(amount_cents, token)
        return PaymentResult(success=success, amount=amount)
```

**When to use:** Integrating third-party libraries, legacy systems, or external
APIs that you cannot modify.

---

## Decorator (Wrapper)

**Problem:** You need to add behavior to an object dynamically without modifying
its class or creating deep inheritance hierarchies.

**Solution:** Wrap the object in another object that adds behavior before or
after delegating to the original.

```python
# Base interface
class DataSource(ABC):
    @abstractmethod
    def read(self) -> str: ...
    @abstractmethod
    def write(self, data: str) -> None: ...

# Concrete implementation
class FileDataSource(DataSource):
    def __init__(self, path: str):
        self.path = path
    def read(self) -> str:
        return open(self.path).read()
    def write(self, data: str) -> None:
        open(self.path, "w").write(data)

# Decorator adds encryption transparently
class EncryptedDataSource(DataSource):
    def __init__(self, wrapped: DataSource, cipher):
        self.wrapped = wrapped
        self.cipher = cipher
    def read(self) -> str:
        return self.cipher.decrypt(self.wrapped.read())
    def write(self, data: str) -> None:
        self.wrapped.write(self.cipher.encrypt(data))

# Decorator adds logging transparently
class LoggedDataSource(DataSource):
    def __init__(self, wrapped: DataSource, logger):
        self.wrapped = wrapped
        self.logger = logger
    def read(self) -> str:
        self.logger.info("data_read", source=str(self.wrapped))
        return self.wrapped.read()
    def write(self, data: str) -> None:
        self.logger.info("data_write", source=str(self.wrapped), size=len(data))
        self.wrapped.write(data)

# Compose decorators
source = LoggedDataSource(EncryptedDataSource(FileDataSource("data.txt"), cipher), logger)
```

---

## Do / Don't

- **Do** use the simplest form of a pattern. A function is a valid Strategy.
- **Do** name classes after the pattern when it aids communication:
  `LegacyPaymentAdapter`, `RetryDecorator`.
- **Do** prefer composition over inheritance for combining behaviors.
- **Don't** apply patterns pre-emptively. Wait until the code shows the need.
- **Don't** create a factory when a constructor call is sufficient.
- **Don't** use Observer when a direct function call is clearer and there is
  only one consumer.
- **Don't** stack more than 2-3 decorators. Beyond that, consider a different
  approach (middleware pipeline, for example).

---

## Common Pitfalls

1. **Pattern fever.** Applying 5 patterns to a 100-line module. The patterns add
   more complexity than the problem warranted. Solution: reach for a pattern only
   when you feel the pain of not having it.
2. **Wrong pattern.** Using Observer when you need a queue (messages must be processed
   exactly once). Solution: match the pattern to the actual requirement.
3. **Abstract everything.** Creating interfaces for every class "in case we need to
   swap it." Solution: follow the Rule of Three. Abstract when you have three
   concrete needs, not one hypothetical one.
4. **Decorator ordering bugs.** The order of nested decorators matters. Logging
   outside encryption sees encrypted data; logging inside sees plaintext. Solution:
   document the expected order. Write a test that verifies the composition.
5. **God factory.** A factory that creates everything in the application, hiding
   the actual dependency graph. Solution: use a proper dependency injection
   container, or keep factories small and focused.

---

## Checklist

- [ ] The pattern solves a real, present problem (not a hypothetical future one)
- [ ] The pattern name is used in class/function names for team communication
- [ ] The simplest form of the pattern is used (function over class when possible)
- [ ] Composition is preferred over inheritance
- [ ] No more than 2-3 decorators are stacked
- [ ] Factories are used only when creation logic is genuinely complex
- [ ] Observer is used only when there are multiple, decoupled consumers
- [ ] Adapters wrap external code -- not your own internal interfaces
- [ ] Pattern usage is consistent across the codebase (one approach per problem type)
