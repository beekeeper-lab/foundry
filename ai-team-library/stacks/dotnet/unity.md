# Unity Development with C#

Patterns and conventions for Unity game development using C#. Covers Unity
2022 LTS+ with modern C# patterns adapted for Unity's runtime constraints.
Unity uses a specialized Mono/.NET runtime and its own component-entity
architecture, so standard .NET conventions require significant adaptation.

---

## Defaults

| Decision                | Default                                          | Alternatives                                |
|-------------------------|--------------------------------------------------|---------------------------------------------|
| Architecture            | Component-based (MonoBehaviour)                  | ECS (DOTS), ScriptableObject architecture   |
| Project layout          | Feature folders under `Assets/_Project/`         | Assembly-definition-based modules           |
| Dependency injection    | None (use ScriptableObject channels)             | VContainer, Zenject/Extenject               |
| Input system            | New Input System (Input Actions)                 | Legacy Input Manager                        |
| UI toolkit              | UI Toolkit (runtime UI)                          | Unity UI (uGUI/Canvas)                      |
| Serialization           | Unity JSON (`JsonUtility`)                       | Newtonsoft.Json, Odin Serializer            |
| Async                   | UniTask                                          | Coroutines, Awaitable (Unity 2023+)         |
| State machines          | ScriptableObject-based states                    | Animator-driven, custom FSM                 |
| Logging                 | `Debug.Log` with conditional compilation         | Unity Logging package, custom logger        |
| Testing                 | Unity Test Framework (NUnit + Play Mode)         | —                                           |
| Version control         | Git with `.gitignore` + Git LFS for binaries     | Unity Version Control (Plastic SCM)         |

---

## Project Structure

```
Assets/
  _Project/                      # All project-specific assets (underscore sorts first)
    Scripts/
      Runtime/
        Characters/
          PlayerController.cs
          EnemyAI.cs
          CharacterStats.cs
        Combat/
          WeaponSystem.cs
          DamageCalculator.cs
          Projectile.cs
        UI/
          HealthBar.cs
          InventoryPanel.cs
          DialogueBox.cs
        Infrastructure/
          GameManager.cs
          AudioManager.cs
          SaveSystem.cs
          ObjectPool.cs
        ScriptableObjects/
          Definitions/
            WeaponDefinition.cs
            EnemyDefinition.cs
          Channels/
            VoidEventChannel.cs
            IntEventChannel.cs
            FloatEventChannel.cs
      Editor/
        CustomInspectors/
        EditorTools/
    Prefabs/
      Characters/
      Environment/
      UI/
    Art/
      Models/
      Textures/
      Materials/
      Animations/
    Audio/
      Music/
      SFX/
    Scenes/
      _Boot.unity                # Bootstrap scene (always loaded first)
      MainMenu.unity
      Gameplay.unity
    Resources/                   # Only for assets that MUST be loaded by name
    Settings/
      InputActions.inputactions
  Plugins/                       # Third-party native plugins
  Tests/
    EditMode/
    PlayMode/
```

**Rules:**
- All project code lives under `Assets/_Project/`. Never scatter scripts at the
  asset root.
- Use Assembly Definition files (`.asmdef`) to split Runtime, Editor, and Tests
  into separate compilation units.
- `Resources/` folder is special — Unity includes everything in it in the build.
  Only put assets there if you genuinely need `Resources.Load()`.
- Binary assets (textures, models, audio) use Git LFS. Add patterns to
  `.gitattributes`.

---

## MonoBehaviour Patterns

### Component Design

```csharp
using UnityEngine;

namespace Company.Game.Characters
{
    [RequireComponent(typeof(Rigidbody2D))]
    [DisallowMultipleComponent]
    public sealed class PlayerController : MonoBehaviour
    {
        [Header("Movement")]
        [SerializeField] private float _moveSpeed = 5f;
        [SerializeField] private float _jumpForce = 10f;

        [Header("Ground Detection")]
        [SerializeField] private Transform _groundCheck;
        [SerializeField] private float _groundCheckRadius = 0.2f;
        [SerializeField] private LayerMask _groundLayer;

        private Rigidbody2D _rb;
        private PlayerInput _input;
        private bool _isGrounded;

        private void Awake()
        {
            _rb = GetComponent<Rigidbody2D>();
            _input = new PlayerInput();
        }

        private void OnEnable()
        {
            _input.Enable();
        }

        private void OnDisable()
        {
            _input.Disable();
        }

        private void FixedUpdate()
        {
            var moveInput = _input.Gameplay.Move.ReadValue<Vector2>();
            _rb.linearVelocity = new Vector2(
                moveInput.x * _moveSpeed,
                _rb.linearVelocity.y);
        }

        private void Update()
        {
            _isGrounded = Physics2D.OverlapCircle(
                _groundCheck.position, _groundCheckRadius, _groundLayer);

            if (_input.Gameplay.Jump.WasPressedThisFrame() && _isGrounded)
            {
                _rb.AddForce(Vector2.up * _jumpForce, ForceMode2D.Impulse);
            }
        }
    }
}
```

### Lifecycle Method Order

```
Awake()           → Cache component references, initialize state
OnEnable()        → Subscribe to events, enable input
Start()           → Initialization that depends on other objects being Awake
Update()          → Per-frame logic, input polling
FixedUpdate()     → Physics, movement (fixed timestep)
LateUpdate()      → Camera follow, post-movement adjustments
OnDisable()       → Unsubscribe from events, disable input
OnDestroy()       → Final cleanup, release unmanaged resources
```

---

## ScriptableObject Architecture

### Data Definitions

```csharp
[CreateAssetMenu(fileName = "New Weapon", menuName = "Game/Weapon Definition")]
public sealed class WeaponDefinition : ScriptableObject
{
    [field: SerializeField] public string WeaponName { get; private set; } = "";
    [field: SerializeField] public int BaseDamage { get; private set; } = 10;
    [field: SerializeField] public float AttackSpeed { get; private set; } = 1f;
    [field: SerializeField] public float Range { get; private set; } = 2f;
    [field: SerializeField] public Sprite Icon { get; private set; }
    [field: SerializeField] public GameObject ProjectilePrefab { get; private set; }
}
```

### Event Channels (decoupled communication)

```csharp
// ScriptableObjects/Channels/VoidEventChannel.cs
[CreateAssetMenu(menuName = "Events/Void Event Channel")]
public sealed class VoidEventChannel : ScriptableObject
{
    private readonly HashSet<System.Action> _listeners = new();

    public void Register(System.Action listener) => _listeners.Add(listener);
    public void Unregister(System.Action listener) => _listeners.Remove(listener);

    public void Raise()
    {
        foreach (var listener in _listeners)
        {
            listener.Invoke();
        }
    }
}

// Generic typed channel
[CreateAssetMenu(menuName = "Events/Int Event Channel")]
public sealed class IntEventChannel : ScriptableObject
{
    private readonly HashSet<System.Action<int>> _listeners = new();

    public void Register(System.Action<int> listener) => _listeners.Add(listener);
    public void Unregister(System.Action<int> listener) => _listeners.Remove(listener);

    public void Raise(int value)
    {
        foreach (var listener in _listeners)
        {
            listener.Invoke(value);
        }
    }
}

// Usage — publisher
public sealed class PlayerHealth : MonoBehaviour
{
    [SerializeField] private IntEventChannel _onHealthChanged;
    [SerializeField] private VoidEventChannel _onPlayerDied;

    private int _currentHealth = 100;

    public void TakeDamage(int amount)
    {
        _currentHealth = Mathf.Max(0, _currentHealth - amount);
        _onHealthChanged.Raise(_currentHealth);

        if (_currentHealth <= 0)
        {
            _onPlayerDied.Raise();
        }
    }
}

// Usage — subscriber
public sealed class HealthBar : MonoBehaviour
{
    [SerializeField] private IntEventChannel _onHealthChanged;
    [SerializeField] private Slider _slider;

    private void OnEnable() => _onHealthChanged.Register(UpdateBar);
    private void OnDisable() => _onHealthChanged.Unregister(UpdateBar);

    private void UpdateBar(int health)
    {
        _slider.value = health / 100f;
    }
}
```

---

## Do / Don't

### Do

- Use `[SerializeField] private` instead of `public` fields for Inspector exposure.
- Use `[RequireComponent]` to enforce component dependencies.
- Use `[DisallowMultipleComponent]` on components that should be singletons per
  GameObject.
- Cache component references in `Awake()` — never call `GetComponent<T>()` in
  `Update()`.
- Use object pooling for frequently instantiated/destroyed objects (projectiles,
  particles, enemies).
- Use `CompareTag("Player")` instead of `gameObject.tag == "Player"` (avoids
  allocation).
- Use Assembly Definition files to control compilation units and reduce
  recompile times.
- Use `#if UNITY_EDITOR` for editor-only code to prevent it from shipping.
- Unsubscribe from events in `OnDisable()` — match every `OnEnable()` subscription.
- Use the New Input System with Input Actions asset for rebindable input.

### Don't

- Don't use `Find()`, `FindObjectOfType()`, or `FindObjectsOfType()` at runtime.
  They are O(n) scene scans. Use direct references or event channels.
- Don't use `SendMessage()` or `BroadcastMessage()` — they use reflection and
  are slow with no compile-time safety.
- Don't allocate in `Update()`. Avoid `new`, string concatenation, LINQ, and
  `foreach` on non-array collections in hot paths.
- Don't use `async void` — use UniTask or coroutines for async operations.
- Don't use singletons via static instances (`Instance = this`). Use
  ScriptableObject channels or a DI container.
- Don't use `Resources.Load()` for general asset loading. Use Addressables or
  direct references.
- Don't nest coroutines deeply. Use UniTask for complex async flows.
- Don't ignore the distinction between `Update` (frame-dependent) and
  `FixedUpdate` (physics timestep). Physics in `FixedUpdate`, input in `Update`.
- Don't use `Camera.main` in `Update()` — it calls `FindObjectWithTag` internally.
  Cache the reference.
- Don't modify `transform.position` directly for physics objects. Use
  `Rigidbody.MovePosition()` or apply forces.

---

## Object Pooling

```csharp
public sealed class ObjectPool : MonoBehaviour
{
    [SerializeField] private GameObject _prefab;
    [SerializeField] private int _initialSize = 20;

    private readonly Queue<GameObject> _pool = new();

    private void Awake()
    {
        for (var i = 0; i < _initialSize; i++)
        {
            var obj = Instantiate(_prefab, transform);
            obj.SetActive(false);
            _pool.Enqueue(obj);
        }
    }

    public GameObject Get(Vector3 position, Quaternion rotation)
    {
        var obj = _pool.Count > 0
            ? _pool.Dequeue()
            : Instantiate(_prefab, transform);

        obj.transform.SetPositionAndRotation(position, rotation);
        obj.SetActive(true);
        return obj;
    }

    public void Return(GameObject obj)
    {
        obj.SetActive(false);
        _pool.Enqueue(obj);
    }
}
```

---

## Performance Patterns

### Avoiding Allocations in Hot Paths

```csharp
// BAD — allocates every frame
private void Update()
{
    var enemies = FindObjectsOfType<Enemy>();          // O(n) + allocation
    var nearby = enemies.Where(e => IsNearby(e));      // LINQ allocation
    Debug.Log($"Found {nearby.Count()} enemies");      // string allocation
}

// GOOD — zero allocation
private readonly Collider[] _hitBuffer = new Collider[32];

private void Update()
{
    var count = Physics.OverlapSphereNonAlloc(
        transform.position, _detectionRadius, _hitBuffer, _enemyLayer);

    for (var i = 0; i < count; i++)
    {
        ProcessEnemy(_hitBuffer[i]);
    }
}
```

### String Operations

```csharp
// BAD — allocates new strings every frame
private void Update()
{
    _scoreText.text = "Score: " + _score.ToString();
}

// GOOD — use StringBuilder or cache
private readonly StringBuilder _sb = new(32);

private void UpdateScore(int score)
{
    _sb.Clear();
    _sb.Append("Score: ");
    _sb.Append(score);
    _scoreText.SetText(_sb);
}
```

---

## Async with UniTask

```csharp
using Cysharp.Threading.Tasks;

public sealed class SceneLoader : MonoBehaviour
{
    public async UniTaskVoid LoadSceneAsync(string sceneName)
    {
        // Show loading screen
        await _loadingScreen.FadeInAsync();

        // Load scene
        await SceneManager.LoadSceneAsync(sceneName)
            .ToUniTask(Progress.Create<float>(p =>
                _loadingBar.value = p));

        // Hide loading screen
        await _loadingScreen.FadeOutAsync();
    }

    // Cancellation support
    public async UniTask<EnemyWave> SpawnWaveAsync(
        WaveDefinition wave, CancellationToken ct)
    {
        foreach (var spawn in wave.Spawns)
        {
            SpawnEnemy(spawn);
            await UniTask.Delay(
                TimeSpan.FromSeconds(spawn.Delay),
                cancellationToken: ct);
        }

        return new EnemyWave(wave.Spawns.Count);
    }
}
```

---

## Save System Pattern

```csharp
public static class SaveSystem
{
    private static readonly string SavePath =
        Path.Combine(Application.persistentDataPath, "save.json");

    public static void Save(GameData data)
    {
        var json = JsonUtility.ToJson(data, prettyPrint: true);
        File.WriteAllText(SavePath, json);
    }

    public static GameData Load()
    {
        if (!File.Exists(SavePath))
            return new GameData();

        var json = File.ReadAllText(SavePath);
        return JsonUtility.FromJson<GameData>(json);
    }
}

[System.Serializable]
public sealed class GameData
{
    public int Level = 1;
    public int Score;
    public float PlayTime;
    public List<string> UnlockedItems = new();
}
```

---

## Common Pitfalls

1. **Garbage collection spikes** — Allocating in `Update()` triggers GC pauses
   that cause visible frame drops. Pre-allocate buffers, avoid LINQ in hot paths,
   and use `NonAlloc` physics methods.
2. **Missing component caching** — Calling `GetComponent<T>()` every frame is
   expensive. Cache references in `Awake()`.
3. **Physics in Update** — Applying forces or setting velocity in `Update()`
   causes inconsistent behavior at different frame rates. Use `FixedUpdate()`
   for all physics operations.
4. **Coroutine leaks** — Starting coroutines without stopping them on
   `OnDisable()` causes null reference exceptions when the object is destroyed.
5. **Serialization traps** — `JsonUtility` doesn't support dictionaries,
   polymorphism, or properties. Use `[Serializable]` classes with public fields
   or switch to Newtonsoft.Json for complex data.
6. **Build size bloat** — Assets in `Resources/` are always included in builds.
   Move assets out of `Resources/` and use Addressables for on-demand loading.
7. **Singleton abuse** — Static singletons create hidden coupling, make testing
   impossible, and cause issues with scene reloading. Use ScriptableObject
   channels or DI containers.
8. **Ignoring Profiler** — Guessing at performance issues instead of profiling.
   Use the Unity Profiler and Frame Debugger before optimizing.
9. **Large scenes** — Putting everything in one scene causes long load times
   and merge conflicts. Use additive scene loading for independent sections.
10. **Camera.main in Update** — `Camera.main` internally calls
    `FindGameObjectWithTag("MainCamera")` every time. Cache the reference.

---

## Alternatives

| Approach             | When to consider                                       |
|----------------------|--------------------------------------------------------|
| DOTS/ECS             | Massive entity counts (10k+), data-oriented performance |
| Godot                | Open-source alternative, lighter-weight for 2D         |
| Unreal Engine        | AAA graphics, large team, C++ preference               |
| Addressables         | When `Resources.Load` becomes a build size problem     |
| VContainer/Zenject   | Large projects needing proper DI and testability       |

---

## Checklist

- [ ] Project assets organized under `Assets/_Project/` with feature folders
- [ ] Assembly Definition files created for Runtime, Editor, and Tests
- [ ] `[SerializeField] private` used instead of `public` for Inspector fields
- [ ] Component references cached in `Awake()`, not fetched in `Update()`
- [ ] Events subscribed in `OnEnable()`, unsubscribed in `OnDisable()`
- [ ] Object pooling used for frequently spawned/despawned objects
- [ ] No `Find*` calls at runtime — use direct references or event channels
- [ ] No allocations in `Update()` / `FixedUpdate()` / `LateUpdate()`
- [ ] Physics operations in `FixedUpdate()`, input in `Update()`
- [ ] New Input System used with Input Actions asset
- [ ] ScriptableObject event channels used for decoupled communication
- [ ] Git LFS configured for binary assets (textures, models, audio)
- [ ] `Resources/` folder contains only assets that require runtime name-based loading
- [ ] Save system uses `Application.persistentDataPath`
- [ ] Profiler used to validate performance before optimization
- [ ] All target platforms tested (standalone, mobile, console)
