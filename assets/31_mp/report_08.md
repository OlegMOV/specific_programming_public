# OPTICS
## Розширення DBSCAN для даних зі змінною щільністю

Ordering Points To Identify the Clustering Structure

<small style="color:#dde">Ankerst, Breunig, Kriegel, Sander · ACM SIGMOD, 1999</small>

---

## План

1. Нагадування: як працює DBSCAN
2. Проблема: змінна щільність
3. Ідея OPTICS
4. Core distance та reachability distance
5. Алгоритм крок за кроком
6. Reachability plot — як читати
7. Витягування кластерів
8. Порівняння DBSCAN vs OPTICS
9. Приклад на Python
10. Складність, переваги, обмеження, застосування

---

## 1. DBSCAN: нагадування

<div class="cols">
<div>

Два параметри:

- **ε (eps)** — радіус околу
- **MinPts** — мінімальна кількість точок в околі

Типи точок:

- 🔵 **Core** — у ε-околі ≥ MinPts точок
- 🟡 **Border** — у околі core-точки, але сама не core
- ⚫ **Noise** — решта

Кластер = множина точок, **досяжних за щільністю**.

</div>
<div>

<svg viewBox="0 0 320 260" width="100%" xmlns="http://www.w3.org/2000/svg">
  <rect width="320" height="260" fill="#fff" stroke="#ccd"/>
  <circle cx="130" cy="120" r="60" fill="#3a8fb7" fill-opacity=".12" stroke="#3a8fb7" stroke-dasharray="5"/>
  <circle cx="190" cy="140" r="60" fill="#3a8fb7" fill-opacity=".12" stroke="#3a8fb7" stroke-dasharray="5"/>
  <g fill="#1f6fb2">
    <circle cx="110" cy="105" r="6"/><circle cx="135" cy="120" r="6"/><circle cx="150" cy="95" r="6"/>
    <circle cx="125" cy="145" r="6"/><circle cx="170" cy="130" r="6"/><circle cx="190" cy="150" r="6"/><circle cx="165" cy="160" r="6"/>
  </g>
  <g fill="#f0b429"><circle cx="228" cy="170" r="6"/><circle cx="85" cy="130" r="6"/></g>
  <g fill="#333"><circle cx="40" cy="40" r="6"/><circle cx="280" cy="50" r="6"/><circle cx="270" cy="220" r="6"/></g>
  <text x="12" y="250" font-size="12" fill="#555">● core  ● border  ● noise</text>
</svg>

</div>
</div>

---

## 2. Проблема: змінна щільність

<div class="cols">
<div>

DBSCAN використовує **один глобальний ε**.

- ε малий → щільні кластери знайдені, **розріджені стають шумом**
- ε великий → розріджені знайдені, **щільні кластери зливаються**

Немає єдиного ε, який підходить для всіх кластерів одночасно.

</div>
<div>

<svg viewBox="0 0 320 240" width="100%" xmlns="http://www.w3.org/2000/svg">
  <rect width="320" height="240" fill="#fff" stroke="#ccd"/>
  <!-- dense cluster A -->
  <g fill="#1f6fb2">
    <circle cx="60" cy="60" r="3"/><circle cx="66" cy="66" r="3"/><circle cx="55" cy="68" r="3"/><circle cx="70" cy="56" r="3"/>
    <circle cx="62" cy="75" r="3"/><circle cx="75" cy="68" r="3"/><circle cx="52" cy="58" r="3"/><circle cx="68" cy="78" r="3"/>
  </g>
  <!-- dense cluster B close to A -->
  <g fill="#c0392b">
    <circle cx="100" cy="70" r="3"/><circle cx="106" cy="76" r="3"/><circle cx="95" cy="78" r="3"/><circle cx="110" cy="66" r="3"/>
    <circle cx="102" cy="85" r="3"/><circle cx="115" cy="78" r="3"/><circle cx="92" cy="68" r="3"/>
  </g>
  <!-- sparse cluster C -->
  <g fill="#2e9e5b">
    <circle cx="220" cy="150" r="3"/><circle cx="260" cy="170" r="3"/><circle cx="240" cy="200" r="3"/>
    <circle cx="200" cy="190" r="3"/><circle cx="270" cy="135" r="3"/><circle cx="235" cy="165" r="3"/><circle cx="215" cy="215" r="3"/>
  </g>
  <circle cx="85" cy="70" r="14" fill="none" stroke="#999" stroke-dasharray="3"/>
  <text x="120" y="40" font-size="11" fill="#555">малий ε: C = шум</text>
  <circle cx="240" cy="170" r="55" fill="none" stroke="#999" stroke-dasharray="3"/>
  <text x="150" y="232" font-size="11" fill="#555">великий ε: A і B зливаються</text>
</svg>

</div>
</div>

---

## 3. Ідея OPTICS

> Замість **одного** розбиття — побудувати **упорядкування** точок, що містить кластерні структури **для всіх ε ≤ ε_max** одночасно.

- OPTICS **не повертає кластери напряму**
- Він повертає **порядок точок** + для кожної точки **reachability distance**
- З цього впорядкування можна отримати кластери для будь-якого ε' ≤ ε_max
- Параметри: **ε_max** (верхня межа) та **MinPts**

![bg right:38% fit](https://commons.wikimedia.org/wiki/Special:FilePath/OPTICS.svg)

<small>Зображення: Wikimedia Commons (OPTICS.svg)</small>

---

## 4. Core distance

**Core distance** точки *p* — мінімальний радіус ε', при якому *p* стає core-точкою:

$$
\text{core-dist}(p) =
\begin{cases}
\text{відстань до } \text{MinPts}\text{-го сусіда} & \text{якщо } |N_{\varepsilon_{max}}(p)| \ge \text{MinPts}\\
\text{не визначена} & \text{інакше}
\end{cases}
$$

<svg viewBox="0 0 640 170" width="80%" xmlns="http://www.w3.org/2000/svg" style="display:block;margin:auto">
  <rect width="640" height="170" fill="#fff" stroke="#ccd"/>
  <circle cx="160" cy="85" r="70" fill="#3a8fb7" fill-opacity=".08" stroke="#3a8fb7" stroke-dasharray="5"/>
  <circle cx="160" cy="85" r="38" fill="#2e9e5b" fill-opacity=".15" stroke="#2e9e5b"/>
  <circle cx="160" cy="85" r="6" fill="#c0392b"/>
  <g fill="#1f6fb2"><circle cx="185" cy="70" r="4"/><circle cx="135" cy="100" r="4"/><circle cx="192" cy="100" r="4"/><circle cx="120" cy="60" r="4"/><circle cx="215" cy="60" r="4"/></g>
  <text x="152" y="78" font-size="11" fill="#c0392b">p</text>
  <text x="250" y="60" font-size="14" fill="#333">ε_max — зовнішнє коло (максимальний радіус пошуку)</text>
  <text x="250" y="90" font-size="14" fill="#2e9e5b">core-dist(p) — внутрішнє коло (MinPts = 4)</text>
  <text x="250" y="120" font-size="14" fill="#555">Чим менша core-dist, тим щільніший регіон навколо p</text>
</svg>

---

## 4. Reachability distance

Досяжність точки *o* з точки *p*:

$$
\text{reach-dist}(o, p) = \max\big(\text{core-dist}(p),\ d(p, o)\big)
$$

- Якщо *o* дуже близько до *p* — береться **core-dist(p)** (не менше за «масштаб щільності» *p*)
- Якщо *o* далеко — береться реальна відстань **d(p, o)**
- Для точки *o* зберігається **мінімум** reach-dist по всіх опрацьованих core-точках

**Інтуїція:** reachability = «наскільки великий ε потрібен, щоб дійти до точки з кластера».

---

## 5. Алгоритм OPTICS

```text
OPTICS(D, ε_max, MinPts):
  для кожної точки p ∈ D:  reach[p] = UNDEFINED, processed[p] = false
  order = []

  для кожної необробленої p ∈ D:
      N = neighbors(p, ε_max); processed[p] = true; order.append(p)
      якщо core-dist(p) визначена:
          Seeds = пріоритетна черга (за reach)
          update(N, p, Seeds)
          поки Seeds не порожня:
              q = Seeds.pop_min_reach()
              N' = neighbors(q, ε_max); processed[q] = true; order.append(q)
              якщо core-dist(q) визначена:
                  update(N', q, Seeds)

update(N, p, Seeds):
  для кожної необробленої o ∈ N:
      new = max(core-dist(p), dist(p, o))
      якщо reach[o] невизначена: reach[o] = new; Seeds.insert(o)
      інакше якщо new < reach[o]: reach[o] = new; Seeds.decrease(o)
```

Результат: **впорядкований список** `(точка, reach-dist)`.

---

## 5. Алгоритм — візуально

<svg viewBox="0 0 760 200" width="100%" xmlns="http://www.w3.org/2000/svg">
  <defs><marker id="a" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 z" fill="#1f4e79"/></marker></defs>
  <g font-size="13" fill="#1f4e79" text-anchor="middle">
    <rect x="10" y="60" width="130" height="70" rx="10" fill="#e8f1f8" stroke="#1f4e79"/><text x="75" y="90">Вибрати</text><text x="75" y="108">необроблену точку</text>
    <rect x="170" y="60" width="130" height="70" rx="10" fill="#e8f1f8" stroke="#1f4e79"/><text x="235" y="90">Знайти ε_max-</text><text x="235" y="108">сусідів, core-dist</text>
    <rect x="330" y="60" width="130" height="70" rx="10" fill="#e8f1f8" stroke="#1f4e79"/><text x="395" y="90">Оновити reach</text><text x="395" y="108">у черзі Seeds</text>
    <rect x="490" y="60" width="130" height="70" rx="10" fill="#e8f1f8" stroke="#1f4e79"/><text x="555" y="90">Взяти точку з</text><text x="555" y="108">мін. reach</text>
    <rect x="650" y="60" width="100" height="70" rx="10" fill="#d9f0e2" stroke="#2e9e5b"/><text x="700" y="90">Додати до</text><text x="700" y="108">порядку</text>
  </g>
  <g stroke="#1f4e79" stroke-width="2" marker-end="url(#a)">
    <line x1="140" y1="95" x2="168" y2="95"/><line x1="300" y1="95" x2="328" y2="95"/>
    <line x1="460" y1="95" x2="488" y2="95"/><line x1="620" y1="95" x2="648" y2="95"/>
  </g>
  <path d="M700 135 Q700 185 395 185 Q395 150 395 135" fill="none" stroke="#999" stroke-dasharray="4" marker-end="url(#a)"/>
  <text x="550" y="180" font-size="12" fill="#666" text-anchor="middle">повторювати, поки Seeds не порожня</text>
</svg>

---

## 6. Reachability plot

<div class="cols">
<div>

<svg viewBox="0 0 360 240" width="100%" xmlns="http://www.w3.org/2000/svg">
  <rect width="360" height="240" fill="#fff" stroke="#ccd"/>
  <line x1="30" y1="210" x2="345" y2="210" stroke="#333"/><line x1="30" y1="20" x2="30" y2="210" stroke="#333"/>
  <!-- cluster A: deep valley -->
  <g fill="#1f6fb2">
    <rect x="40" y="170" width="6" height="40"/><rect x="48" y="176" width="6" height="34"/><rect x="56" y="172" width="6" height="38"/>
    <rect x="64" y="178" width="6" height="32"/><rect x="72" y="174" width="6" height="36"/><rect x="80" y="180" width="6" height="30"/>
  </g>
  <!-- peak -->
  <rect x="88" y="60" width="6" height="150" fill="#555"/>
  <!-- cluster B: shallow valley (sparser) -->
  <g fill="#c0392b">
    <rect x="96" y="120" width="6" height="90"/><rect x="104" y="128" width="6" height="82"/><rect x="112" y="124" width="6" height="86"/>
    <rect x="120" y="132" width="6" height="78"/><rect x="128" y="126" width="6" height="84"/><rect x="136" y="130" width="6" height="80"/><rect x="144" y="122" width="6" height="88"/>
  </g>
  <rect x="152" y="40" width="6" height="170" fill="#555"/>
  <!-- cluster C: deep valley -->
  <g fill="#2e9e5b">
    <rect x="160" y="165" width="6" height="45"/><rect x="168" y="172" width="6" height="38"/><rect x="176" y="168" width="6" height="42"/>
    <rect x="184" y="176" width="6" height="34"/><rect x="192" y="170" width="6" height="40"/><rect x="200" y="174" width="6" height="36"/>
  </g>
  <g fill="#555"><rect x="208" y="30" width="6" height="180"/><rect x="216" y="50" width="6" height="160"/><rect x="224" y="25" width="6" height="185"/><rect x="232" y="45" width="6" height="165"/></g>
  <line x1="30" y1="150" x2="345" y2="150" stroke="#f0b429" stroke-dasharray="5"/>
  <text x="300" y="145" font-size="11" fill="#b8860b">ε' = 150</text>
  <text x="34" y="14" font-size="11" fill="#333">reachability distance</text>
  <text x="250" y="230" font-size="11" fill="#333">порядок точок →</text>
</svg>

</div>
<div>

**Як читати:**

- **Долини** = кластери (точки близько одна до одної за досяжністю)
- **Глибока долина** = щільний кластер
- **Мілка долина** = розріджений кластер
- **Піки** = межі між кластерами / шум
- **Горизонтальна лінія ε'** «розрізає» графік → отримуємо DBSCAN-розбиття для цього ε'
- **Вкладені долини** = ієрархія кластерів

</div>
</div>

---

## 7. Витягування кластерів

Два основні підходи:

| Метод | Ідея |
|---|---|
| **ε'-cut (DBSCAN-подібний)** | Горизонтальний поріг: точки з reach ≤ ε' утворюють кластери |
| **ξ-метод (xi)** | Шукає **стрімкі спади/підйоми** (відносна зміна ≥ ξ) → автоматично знаходить кластери різної щільності та ієрархію |

Ключові параметри ξ-методу: `xi` (0–1), `min_cluster_size`.

> Один раз побудований OPTICS-порядок → багато різних кластеризацій **без перерахунку**.

---

## 8. DBSCAN vs OPTICS

| Критерій | DBSCAN | OPTICS |
|---|---|---|
| Щільність кластерів | Одна (глобальний ε) | **Змінна** |
| Параметри | ε, MinPts | ε_max, MinPts (+ ξ для витягування) |
| Результат | Плоске розбиття | **Упорядкування + ієрархія** |
| Чутливість до ε | Висока | Низька (ε_max лише верхня межа) |
| Візуалізація структури | Немає | **Reachability plot** |
| Складність | O(n log n) з індексом | O(n log n) з індексом, **більші константи** |
| Пам'ять | O(n) | O(n) |
| Простота | Висока | Середня |

---

## 9. Приклад на Python

```python
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import OPTICS, DBSCAN
from sklearn.datasets import make_blobs

# Дані з різною щільністю
X, _ = make_blobs(
    n_samples=[300, 300, 150],
    centers=[[0, 0], [5, 5], [-5, 6]],
    cluster_std=[0.4, 1.0, 1.8],   # щільний, середній, розріджений
    random_state=42,
)

optics = OPTICS(min_samples=10, xi=0.05, min_cluster_size=0.05).fit(X)
dbscan = DBSCAN(eps=0.6, min_samples=10).fit(X)

fig, ax = plt.subplots(1, 3, figsize=(16, 4.5))

# 1. Reachability plot
reach = optics.reachability_[optics.ordering_]
ax[0].bar(range(len(reach)), reach, width=1.0, color="steelblue")
ax[0].set_title("Reachability plot (OPTICS)")

# 2. OPTICS
ax[1].scatter(*X.T, c=optics.labels_, cmap="tab10", s=8)
ax[1].set_title(f"OPTICS: {optics.labels_.max() + 1} кластерів")

# 3. DBSCAN
ax[2].scatter(*X.T, c=dbscan.labels_, cmap="tab10", s=8)
ax[2].set_title(f"DBSCAN (eps=0.6): {dbscan.labels_.max() + 1} кластерів")

plt.tight_layout()
plt.show()
```

---

## 9. Очікуваний результат

<svg viewBox="0 0 760 230" width="100%" xmlns="http://www.w3.org/2000/svg">
  <g font-size="13" fill="#1f4e79" text-anchor="middle">
    <rect x="5" y="5" width="240" height="190" fill="#fff" stroke="#ccd"/>
    <rect x="260" y="5" width="240" height="190" fill="#fff" stroke="#ccd"/>
    <rect x="515" y="5" width="240" height="190" fill="#fff" stroke="#ccd"/>
    <text x="125" y="215">Reachability plot</text><text x="380" y="215">OPTICS: 3 кластери</text><text x="635" y="215">DBSCAN: розріджений = шум</text>
  </g>
  <!-- plot 1 -->
  <g fill="#1f6fb2"><rect x="20" y="150" width="4" height="40"/><rect x="26" y="155" width="4" height="35"/><rect x="32" y="152" width="4" height="38"/><rect x="38" y="158" width="4" height="32"/><rect x="44" y="154" width="4" height="36"/></g>
  <rect x="52" y="30" width="4" height="160" fill="#555"/>
  <g fill="#c0392b"><rect x="58" y="110" width="4" height="80"/><rect x="64" y="118" width="4" height="72"/><rect x="70" y="112" width="4" height="78"/><rect x="76" y="120" width="4" height="70"/><rect x="82" y="114" width="4" height="76"/><rect x="88" y="119" width="4" height="71"/></g>
  <rect x="96" y="40" width="4" height="150" fill="#555"/>
  <g fill="#2e9e5b"><rect x="102" y="80" width="4" height="110"/><rect x="108" y="88" width="4" height="102"/><rect x="114" y="82" width="4" height="108"/><rect x="120" y="90" width="4" height="100"/><rect x="126" y="84" width="4" height="106"/><rect x="132" y="92" width="4" height="98"/><rect x="138" y="86" width="4" height="104"/></g>
  <!-- scatter OPTICS -->
  <g fill="#1f6fb2"><circle cx="320" cy="140" r="2.5"/><circle cx="324" cy="144" r="2.5"/><circle cx="318" cy="146" r="2.5"/><circle cx="326" cy="138" r="2.5"/><circle cx="322" cy="150" r="2.5"/><circle cx="316" cy="140" r="2.5"/></g>
  <g fill="#c0392b"><circle cx="420" cy="80" r="2.5"/><circle cx="430" cy="90" r="2.5"/><circle cx="415" cy="95" r="2.5"/><circle cx="440" cy="75" r="2.5"/><circle cx="425" cy="105" r="2.5"/><circle cx="445" cy="95" r="2.5"/><circle cx="410" cy="82" r="2.5"/></g>
  <g fill="#2e9e5b"><circle cx="290" cy="45" r="2.5"/><circle cx="320" cy="60" r="2.5"/><circle cx="300" cy="75" r="2.5"/><circle cx="275" cy="62" r="2.5"/><circle cx="335" cy="40" r="2.5"/><circle cx="310" cy="95" r="2.5"/><circle cx="280" cy="85" r="2.5"/></g>
  <!-- scatter DBSCAN -->
  <g fill="#1f6fb2"><circle cx="575" cy="140" r="2.5"/><circle cx="579" cy="144" r="2.5"/><circle cx="573" cy="146" r="2.5"/><circle cx="581" cy="138" r="2.5"/><circle cx="577" cy="150" r="2.5"/></g>
  <g fill="#c0392b"><circle cx="675" cy="80" r="2.5"/><circle cx="685" cy="90" r="2.5"/><circle cx="670" cy="95" r="2.5"/><circle cx="695" cy="75" r="2.5"/></g>
  <g fill="#aaa"><circle cx="545" cy="45" r="2.5"/><circle cx="575" cy="60" r="2.5"/><circle cx="555" cy="75" r="2.5"/><circle cx="530" cy="62" r="2.5"/><circle cx="590" cy="40" r="2.5"/><circle cx="565" cy="95" r="2.5"/><circle cx="700" cy="120" r="2.5"/><circle cx="660" cy="125" r="2.5"/></g>
</svg>

<small>Схематична ілюстрація: сірі точки в DBSCAN — шум, який OPTICS відносить до кластера.</small>

---

## 10. Складність і практичні поради

**Складність**

- З просторовим індексом (k-d tree, ball tree): **O(n log n)**
- Без індексу: **O(n²)**
- Пам'ять: **O(n)**

**Поради**

- `min_samples` — основний регулятор «гладкості» графіка (типово 5–20)
- `max_eps = ∞` — безпечний, але повільніший вибір; обмеження пришвидшує
- Масштабуйте ознаки (`StandardScaler`) — OPTICS чутливий до метрики
- Дивіться на reachability plot **перед** вибором ξ / ε'
- Для великих даних: HDBSCAN як швидша альтернатива

---

## 11. Переваги та обмеження

<div class="cols">
<div>

### ✅ Переваги

- Кластери **різної щільності**
- Немає потреби підбирати точний ε
- Ієрархічна структура кластерів
- Reachability plot — наочна діагностика
- Виявляє шум, довільні форми
- Одне обчислення → багато розбиттів

</div>
<div>

### ⚠️ Обмеження

- Повільніший за DBSCAN
- Складніше інтерпретувати
- Потрібне витягування кластерів (ξ / ε')
- Чутливий до масштабу та метрики
- Погано в просторах високої розмірності («прокляття розмірності»)
- Межі кластерів можуть бути нечіткими

</div>
</div>

---

## 12. Застосування

<div class="cols">
<div>

- 🛰️ **Геоданні** — виявлення міських агломерацій різної густоти
- 🧬 **Біоінформатика** — групи генів / клітин (scRNA-seq)
- 🛡️ **Кібербезпека** — аномалії в мережевому трафіку
- 🛒 **Маркетинг** — сегментація клієнтів
- 🌌 **Астрономія** — скупчення зірок і галактик

</div>
<div>

![Зоряне скупчення](https://commons.wikimedia.org/wiki/Special:FilePath/Pleiades_large.jpg)

<small>Фото: Плеяди — приклад природних кластерів різної щільності (Wikimedia Commons / NASA)</small>

</div>
</div>

---

## Висновки

1. **DBSCAN** — швидкий, але з одним глобальним ε
2. **OPTICS** будує **упорядкування за досяжністю**, а не фіксоване розбиття
3. **Reachability plot** показує кластери, їхню щільність та ієрархію
4. Підходить для даних **зі змінною щільністю**
5. Ціна — більша складність і потреба в окремому етапі витягування кластерів

<br>

**Дякую за увагу! Запитання?**

---

## Література

- Ankerst M., Breunig M., Kriegel H.-P., Sander J. *OPTICS: Ordering Points To Identify the Clustering Structure.* ACM SIGMOD, 1999.
- Ester M. et al. *A Density-Based Algorithm for Discovering Clusters.* KDD, 1996.
- Campello R. et al. *Density-Based Clustering Based on Hierarchical Density Estimates (HDBSCAN).* PAKDD, 2013.
- scikit-learn documentation: `sklearn.cluster.OPTICS`
- Wikipedia: *OPTICS algorithm*
