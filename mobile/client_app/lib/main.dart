import 'dart:ui';

import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';

void main() {
  runApp(const DemiResultsClientApp());
}

class AppColors {
  static const navy = Color(0xFF081526);
  static const mid = Color(0xFF24456F);
  static const accent = Color(0xFFBFD8FB);
  static const soft = Color(0xFFE6F0FB);
  static const bg = Color(0xFFF6F8FB);
  static const muted = Color(0xFF929BAD);
  static const line = Color(0xFFD9E3EF);
}

class Product {
  const Product({
    required this.id,
    required this.brand,
    required this.name,
    required this.category,
    required this.price,
    required this.description,
    required this.usage,
    this.rating = 4.9,
  });

  final int id;
  final String brand;
  final String name;
  final String category;
  final int price;
  final String description;
  final String usage;
  final double rating;
}

class CartLine {
  const CartLine({required this.product, required this.quantity});

  final Product product;
  final int quantity;

  CartLine copyWith({int? quantity}) {
    return CartLine(product: product, quantity: quantity ?? this.quantity);
  }
}

class Consultation {
  const Consultation({
    required this.time,
    required this.specialist,
    required this.concern,
  });

  final DateTime time;
  final String specialist;
  final String concern;
}

enum AppTab { home, catalog, ai, routine, profile }

class DemiResultsClientApp extends StatelessWidget {
  const DemiResultsClientApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'DemiResults',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: AppColors.mid),
        scaffoldBackgroundColor: AppColors.bg,
        fontFamily: 'SF Pro Display',
        useMaterial3: true,
      ),
      home: const ClientShell(),
    );
  }
}

class ClientShell extends StatefulWidget {
  const ClientShell({super.key});

  @override
  State<ClientShell> createState() => _ClientShellState();
}

class _ClientShellState extends State<ClientShell> {
  final products = const [
    Product(
      id: 1,
      brand: 'DemiLab',
      name: 'Gentle Cleansing Gel',
      category: 'Очищение',
      price: 890,
      description: 'Мягкий гель для ежедневного очищения кожи без стянутости.',
      usage: 'Нанести на влажную кожу, вспенить, смыть водой.',
    ),
    Product(
      id: 2,
      brand: 'DemiLab',
      name: 'Barrier Repair Cream',
      category: 'Увлажнение',
      price: 1450,
      description: 'Крем для восстановления защитного барьера кожи.',
      usage: 'Использовать утром и вечером после сыворотки.',
    ),
    Product(
      id: 3,
      brand: 'SkinTheory',
      name: 'Niacinamide Serum 10%',
      category: 'Сыворотки',
      price: 1190,
      description: 'Сыворотка для себорегуляции и ровного тона.',
      usage: 'Нанести 2-3 капли перед кремом.',
    ),
    Product(
      id: 4,
      brand: 'SunCare KG',
      name: 'Daily SPF 50',
      category: 'SPF',
      price: 1590,
      description: 'Лёгкий дневной SPF для города без белого оттенка.',
      usage: 'Нанести за 15 минут до выхода и обновлять днём.',
    ),
  ];

  AppTab tab = AppTab.home;
  String category = 'Все';
  String search = '';
  bool darkTheme = false;
  bool onboarded = false;
  final favoriteIds = <int>{};
  final cart = <int, CartLine>{};
  final routineDone = <String>{'Умывание', 'Тонер', 'Двойное очищение'};
  final consultations = <Consultation>[
    Consultation(
      time: DateTime(2026, 6, 6, 14, 30),
      specialist: 'Айдана',
      concern: 'сухость и лёгкие воспаления',
    ),
  ];

  List<Product> get filteredProducts {
    return products.where((product) {
      final byCategory = category == 'Все' || product.category == category;
      final haystack = '${product.brand} ${product.name} ${product.description}'.toLowerCase();
      return byCategory && haystack.contains(search.toLowerCase());
    }).toList();
  }

  int get cartCount => cart.values.fold(0, (sum, line) => sum + line.quantity);
  int get cartTotal => cart.values.fold(0, (sum, line) => sum + line.product.price * line.quantity);

  void addToCart(Product product) {
    setState(() {
      final line = cart[product.id];
      cart[product.id] = line == null ? CartLine(product: product, quantity: 1) : line.copyWith(quantity: line.quantity + 1);
    });
  }

  void changeQuantity(Product product, int delta) {
    setState(() {
      final line = cart[product.id];
      if (line == null) return;
      final quantity = line.quantity + delta;
      if (quantity <= 0) {
        cart.remove(product.id);
      } else {
        cart[product.id] = line.copyWith(quantity: quantity);
      }
    });
  }

  void toggleFavorite(Product product) {
    setState(() {
      if (!favoriteIds.remove(product.id)) favoriteIds.add(product.id);
    });
  }

  void openProduct(Product product) {
    showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => ProductSheet(product: product, onAdd: () => addToCart(product)),
    );
  }

  @override
  Widget build(BuildContext context) {
    final page = switch (tab) {
      AppTab.home => HomeScreen(
          products: products,
          consultation: consultations.firstOrNull,
          routineDone: routineDone.length,
          routineTotal: 8,
          onOpenAi: () => setState(() => tab = AppTab.ai),
          onOpenCatalog: () => setState(() => tab = AppTab.catalog),
          onOpenRoutine: () => setState(() => tab = AppTab.routine),
          onProduct: openProduct,
          onAdd: addToCart,
          onFavorite: toggleFavorite,
          favoriteIds: favoriteIds,
        ),
      AppTab.catalog => CatalogScreen(
          products: filteredProducts,
          categories: ['Все', 'Очищение', 'Увлажнение', 'SPF', 'Сыворотки'],
          activeCategory: category,
          search: search,
          favoriteIds: favoriteIds,
          cartCount: cartCount,
          favoriteCount: favoriteIds.length,
          onSearch: (value) => setState(() => search = value),
          onCategory: (value) => setState(() => category = value),
          onFavorite: toggleFavorite,
          onAdd: addToCart,
          onProduct: openProduct,
          onCart: openCart,
          onFavorites: openFavorites,
        ),
      AppTab.ai => AiScreen(products: products, onAdd: addToCart),
      AppTab.routine => RoutineScreen(
          done: routineDone,
          consultations: consultations,
          onToggle: (title) => setState(() {
            if (!routineDone.remove(title)) routineDone.add(title);
          }),
        ),
      AppTab.profile => ProfileScreen(
          darkTheme: darkTheme,
          ordersCount: 0,
          consultationsCount: consultations.length,
          onTheme: (value) => setState(() => darkTheme = value),
          onOrders: openOrders,
          onConsultations: openConsultationHistory,
        ),
    };

    return AnimatedThemeShell(
      dark: darkTheme,
      child: Scaffold(
        body: Stack(
          children: [
            AnimatedSwitcher(
              duration: const Duration(milliseconds: 320),
              switchInCurve: Curves.easeOutCubic,
              switchOutCurve: Curves.easeInCubic,
              child: KeyedSubtree(key: ValueKey(tab), child: page),
            ),
            Positioned(
              left: 20,
              right: 20,
              bottom: 12 + MediaQuery.paddingOf(context).bottom,
              child: LiquidBottomNav(
                active: tab,
                onChanged: (value) => setState(() => tab = value),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void openCart() {
    Navigator.of(context).push(
      CupertinoPageRoute<void>(
        builder: (_) => CartScreen(
          lines: cart.values.toList(),
          total: cartTotal,
          onInc: (product) => changeQuantity(product, 1),
          onDec: (product) => changeQuantity(product, -1),
          onRemove: (product) => changeQuantity(product, -999),
        ),
      ),
    );
  }

  void openFavorites() {
    Navigator.of(context).push(
      CupertinoPageRoute<void>(
        builder: (_) => FavoritesScreen(
          products: products.where((product) => favoriteIds.contains(product.id)).toList(),
          favoriteIds: favoriteIds,
          cartCount: cartCount,
          onFavorite: toggleFavorite,
          onAdd: addToCart,
          onProduct: openProduct,
          onCart: openCart,
        ),
      ),
    );
  }

  void openOrders() {
    Navigator.of(context).push(CupertinoPageRoute<void>(builder: (_) => const SimpleHistoryScreen(title: 'История заказов', empty: 'Заказов пока нет')));
  }

  void openConsultationHistory() {
    Navigator.of(context).push(
      CupertinoPageRoute<void>(
        builder: (_) => ConsultationHistoryScreen(consultations: consultations),
      ),
    );
  }
}

class AnimatedThemeShell extends StatelessWidget {
  const AnimatedThemeShell({required this.dark, required this.child, super.key});

  final bool dark;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return AnimatedContainer(
      duration: const Duration(milliseconds: 260),
      color: dark ? AppColors.navy : AppColors.bg,
      child: Theme(
        data: Theme.of(context).copyWith(
          scaffoldBackgroundColor: dark ? AppColors.navy : AppColors.bg,
          textTheme: Theme.of(context).textTheme.apply(
                bodyColor: dark ? Colors.white : AppColors.navy,
                displayColor: dark ? Colors.white : AppColors.navy,
              ),
        ),
        child: child,
      ),
    );
  }
}

class HomeScreen extends StatelessWidget {
  const HomeScreen({
    required this.products,
    required this.consultation,
    required this.routineDone,
    required this.routineTotal,
    required this.onOpenAi,
    required this.onOpenCatalog,
    required this.onOpenRoutine,
    required this.onProduct,
    required this.onAdd,
    required this.onFavorite,
    required this.favoriteIds,
    super.key,
  });

  final List<Product> products;
  final Consultation? consultation;
  final int routineDone;
  final int routineTotal;
  final VoidCallback onOpenAi;
  final VoidCallback onOpenCatalog;
  final VoidCallback onOpenRoutine;
  final ValueChanged<Product> onProduct;
  final ValueChanged<Product> onAdd;
  final ValueChanged<Product> onFavorite;
  final Set<int> favoriteIds;

  @override
  Widget build(BuildContext context) {
    return AppScrollView(
      children: [
        Header(title: 'Ваш персональный уход', eyebrow: 'DemiResults', trailing: IconButton(onPressed: () {}, icon: const Icon(CupertinoIcons.refresh))),
        HeroCareCard(onOpenAi: onOpenAi),
        const SizedBox(height: 14),
        StatsRow(consultation: consultation, routineDone: routineDone, routineTotal: routineTotal),
        const SizedBox(height: 18),
        AiQuestionCard(onTap: onOpenAi),
        SectionTitle(title: 'Популярное', action: 'Все', onAction: onOpenCatalog),
        SizedBox(
          height: 320,
          child: ListView.separated(
            scrollDirection: Axis.horizontal,
            itemCount: products.length,
            separatorBuilder: (_, __) => const SizedBox(width: 14),
            itemBuilder: (context, index) {
              final product = products[index];
              return SizedBox(
                width: 178,
                child: ProductCard(
                  product: product,
                  favorite: favoriteIds.contains(product.id),
                  onFavorite: () => onFavorite(product),
                  onAdd: () => onAdd(product),
                  onTap: () => onProduct(product),
                ),
              );
            },
          ),
        ),
        const SectionTitle(title: 'Акции'),
        const PromoRow(),
        RoutineStrip(done: routineDone, total: routineTotal, onTap: onOpenRoutine),
      ],
    );
  }
}

class CatalogScreen extends StatelessWidget {
  const CatalogScreen({
    required this.products,
    required this.categories,
    required this.activeCategory,
    required this.search,
    required this.favoriteIds,
    required this.cartCount,
    required this.favoriteCount,
    required this.onSearch,
    required this.onCategory,
    required this.onFavorite,
    required this.onAdd,
    required this.onProduct,
    required this.onCart,
    required this.onFavorites,
    super.key,
  });

  final List<Product> products;
  final List<String> categories;
  final String activeCategory;
  final String search;
  final Set<int> favoriteIds;
  final int cartCount;
  final int favoriteCount;
  final ValueChanged<String> onSearch;
  final ValueChanged<String> onCategory;
  final ValueChanged<Product> onFavorite;
  final ValueChanged<Product> onAdd;
  final ValueChanged<Product> onProduct;
  final VoidCallback onCart;
  final VoidCallback onFavorites;

  @override
  Widget build(BuildContext context) {
    return AppScrollView(
      children: [
        Header(
          title: 'Средства',
          eyebrow: 'Каталог',
          trailing: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              BadgeIconButton(icon: CupertinoIcons.heart, count: favoriteCount, onTap: onFavorites),
              const SizedBox(width: 8),
              BadgeIconButton(icon: CupertinoIcons.bag, count: cartCount, onTap: onCart),
            ],
          ),
        ),
        SearchBox(value: search, onChanged: onSearch),
        const SizedBox(height: 14),
        SizedBox(
          height: 38,
          child: ListView.separated(
            scrollDirection: Axis.horizontal,
            itemCount: categories.length,
            separatorBuilder: (_, __) => const SizedBox(width: 8),
            itemBuilder: (context, index) {
              final item = categories[index];
              return ChoiceChip(
                selected: item == activeCategory,
                label: Text(item),
                onSelected: (_) => onCategory(item),
                selectedColor: AppColors.navy,
                labelStyle: TextStyle(color: item == activeCategory ? Colors.white : AppColors.mid, fontWeight: FontWeight.w800),
                backgroundColor: Colors.white,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(999), side: const BorderSide(color: AppColors.line)),
              );
            },
          ),
        ),
        const SizedBox(height: 18),
        ProductGrid(
          products: products,
          favoriteIds: favoriteIds,
          onFavorite: onFavorite,
          onAdd: onAdd,
          onProduct: onProduct,
        ),
      ],
    );
  }
}

class FavoritesScreen extends StatelessWidget {
  const FavoritesScreen({
    required this.products,
    required this.favoriteIds,
    required this.cartCount,
    required this.onFavorite,
    required this.onAdd,
    required this.onProduct,
    required this.onCart,
    super.key,
  });

  final List<Product> products;
  final Set<int> favoriteIds;
  final int cartCount;
  final ValueChanged<Product> onFavorite;
  final ValueChanged<Product> onAdd;
  final ValueChanged<Product> onProduct;
  final VoidCallback onCart;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: AppScrollView(
        children: [
          Header(
            title: 'Любимые средства',
            eyebrow: 'Избранное',
            leading: BackButtonGlass(onTap: () => Navigator.pop(context)),
            trailing: BadgeIconButton(icon: CupertinoIcons.bag, count: cartCount, onTap: onCart),
          ),
          if (products.isEmpty)
            const EmptyPanel(title: 'Избранного пока нет', text: 'Нажмите сердечко в каталоге, чтобы сохранить средство.')
          else
            ProductGrid(
              products: products,
              favoriteIds: favoriteIds,
              onFavorite: onFavorite,
              onAdd: onAdd,
              onProduct: onProduct,
            ),
        ],
      ),
    );
  }
}

class CartScreen extends StatelessWidget {
  const CartScreen({
    required this.lines,
    required this.total,
    required this.onInc,
    required this.onDec,
    required this.onRemove,
    super.key,
  });

  final List<CartLine> lines;
  final int total;
  final ValueChanged<Product> onInc;
  final ValueChanged<Product> onDec;
  final ValueChanged<Product> onRemove;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: AppScrollView(
        children: [
          Header(title: 'Ваш заказ', eyebrow: 'Корзина', leading: BackButtonGlass(onTap: () => Navigator.pop(context))),
          if (lines.isEmpty)
            const EmptyPanel(title: 'Корзина пустая', text: 'Добавьте уход из каталога или избранного.')
          else
            ...lines.map(
              (line) => CartTile(
                line: line,
                onInc: () => onInc(line.product),
                onDec: () => onDec(line.product),
                onRemove: () => onRemove(line.product),
              ),
            ),
          const SizedBox(height: 12),
          LiquidPanel(
            child: Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('Итого', style: TextStyle(color: AppColors.muted, fontWeight: FontWeight.w700)),
                      Text('${formatMoney(total)} сом', style: const TextStyle(fontSize: 24, fontWeight: FontWeight.w900)),
                    ],
                  ),
                ),
                FilledButton(onPressed: lines.isEmpty ? null : () {}, child: const Text('Оформить')),
              ],
            ),
          ),
          const SizedBox(height: 12),
          const CheckoutFields(),
        ],
      ),
    );
  }
}

class AiScreen extends StatefulWidget {
  const AiScreen({required this.products, required this.onAdd, super.key});

  final List<Product> products;
  final ValueChanged<Product> onAdd;

  @override
  State<AiScreen> createState() => _AiScreenState();
}

class _AiScreenState extends State<AiScreen> {
  final messages = <Widget>[
    const ChatBubble.ai(text: 'Расскажите, что сейчас беспокоит кожу: сухость, высыпания, пигментация или чувствительность?'),
    const ChatBubble.user(text: 'Хочу мягкий уход и SPF на каждый день.'),
  ];
  final controller = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Expanded(
          child: AppScrollView(
            bottomPadding: 24,
            children: [
              const Header(title: 'Skincare assistant', eyebrow: 'AI-консультант'),
              const AiHero(),
              const SizedBox(height: 12),
              ...messages,
            ],
          ),
        ),
        Padding(
          padding: EdgeInsets.fromLTRB(20, 0, 20, 100 + MediaQuery.paddingOf(context).bottom),
          child: LiquidPanel(
            padding: const EdgeInsets.all(10),
            radius: 26,
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: controller,
                    decoration: const InputDecoration(border: InputBorder.none, hintText: 'Напишите вопрос...'),
                  ),
                ),
                IconButton.filled(
                  onPressed: send,
                  icon: const Icon(CupertinoIcons.arrow_up),
                  style: IconButton.styleFrom(backgroundColor: AppColors.accent, foregroundColor: AppColors.navy),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  void send() {
    final text = controller.text.trim();
    if (text.isEmpty) return;
    final recommended = widget.products.take(2).toList();
    setState(() {
      messages.add(ChatBubble.user(text: text));
      messages.add(ChatBubble.aiRecommendation(products: recommended, onAdd: widget.onAdd));
      controller.clear();
    });
  }
}

class RoutineScreen extends StatelessWidget {
  const RoutineScreen({required this.done, required this.consultations, required this.onToggle, super.key});

  final Set<String> done;
  final List<Consultation> consultations;
  final ValueChanged<String> onToggle;

  static const morning = ['Умывание', 'Тонер', 'Увлажняющий крем', 'SPF защита'];
  static const evening = ['Двойное очищение', 'Сыворотка', 'Ночной крем'];

  @override
  Widget build(BuildContext context) {
    final all = [...morning, ...evening, 'Успокаивающая маска'];
    return AppScrollView(
      children: [
        const Header(title: 'Ваш план', eyebrow: 'Уход'),
        RoutineHero(done: done.length, total: all.length),
        RoutineGroup(title: 'Утренний уход', icon: CupertinoIcons.sun_max, steps: morning, done: done, onToggle: onToggle),
        RoutineGroup(title: 'Вечерний уход', icon: CupertinoIcons.moon, steps: evening, done: done, onToggle: onToggle),
        const SectionTitle(title: 'Запись к консультанту'),
        if (consultations.isEmpty)
          const EmptyPanel(title: 'Записей нет', text: 'Выберите время консультации после подключения backend.')
        else
          ...consultations.map((item) => ConsultationTile(item: item)),
      ],
    );
  }
}

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({
    required this.darkTheme,
    required this.ordersCount,
    required this.consultationsCount,
    required this.onTheme,
    required this.onOrders,
    required this.onConsultations,
    super.key,
  });

  final bool darkTheme;
  final int ordersCount;
  final int consultationsCount;
  final ValueChanged<bool> onTheme;
  final VoidCallback onOrders;
  final VoidCallback onConsultations;

  @override
  Widget build(BuildContext context) {
    return AppScrollView(
      children: [
        const ProfileHeader(),
        const ProfileForm(),
        const BonusCard(),
        ProfileLink(title: 'История заказов', value: '$ordersCount заказов', onTap: onOrders),
        ProfileLink(title: 'История консультаций', value: '$consultationsCount записей', onTap: onConsultations),
        LiquidPanel(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SectionCaption('Настройки темы'),
              const SizedBox(height: 12),
              SegmentedButton<bool>(
                segments: const [
                  ButtonSegment(value: false, label: Text('Светлая')),
                  ButtonSegment(value: true, label: Text('Тёмная')),
                ],
                selected: {darkTheme},
                onSelectionChanged: (value) => onTheme(value.first),
              ),
            ],
          ),
        ),
        const CardBindingPanel(),
      ],
    );
  }
}

class LiquidBottomNav extends StatelessWidget {
  const LiquidBottomNav({required this.active, required this.onChanged, super.key});

  final AppTab active;
  final ValueChanged<AppTab> onChanged;

  @override
  Widget build(BuildContext context) {
    final items = [
      (AppTab.home, CupertinoIcons.house, 'Главная'),
      (AppTab.catalog, CupertinoIcons.square_grid_2x2, 'Каталог'),
      (AppTab.ai, CupertinoIcons.sparkles, 'AI'),
      (AppTab.routine, CupertinoIcons.circle_grid_hex, 'Уход'),
      (AppTab.profile, CupertinoIcons.person_circle, 'Профиль'),
    ];

    return LiquidPanel(
      padding: const EdgeInsets.all(8),
      radius: 30,
      child: Row(
        children: items.map((item) {
          final selected = item.$1 == active;
          return Expanded(
            child: GestureDetector(
              onTap: () => onChanged(item.$1),
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 360),
                curve: Curves.easeOutCubic,
                height: 58,
                decoration: BoxDecoration(
                  color: selected ? AppColors.accent.withOpacity(0.52) : Colors.transparent,
                  borderRadius: BorderRadius.circular(22),
                  boxShadow: selected ? [BoxShadow(color: AppColors.mid.withOpacity(0.16), blurRadius: 24, offset: const Offset(0, 8))] : null,
                ),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    AnimatedContainer(
                      duration: const Duration(milliseconds: 260),
                      width: item.$1 == AppTab.ai ? 34 : 22,
                      height: item.$1 == AppTab.ai ? 34 : 22,
                      decoration: item.$1 == AppTab.ai
                          ? BoxDecoration(color: AppColors.navy, borderRadius: BorderRadius.circular(14))
                          : null,
                      child: Icon(item.$2, size: item.$1 == AppTab.ai ? 18 : 18, color: item.$1 == AppTab.ai ? AppColors.accent : (selected ? AppColors.navy : AppColors.muted)),
                    ),
                    const SizedBox(height: 3),
                    Text(item.$3, style: TextStyle(fontSize: 10, fontWeight: FontWeight.w800, color: selected ? AppColors.navy : AppColors.muted)),
                  ],
                ),
              ),
            ),
          );
        }).toList(),
      ),
    );
  }
}

class LiquidPanel extends StatelessWidget {
  const LiquidPanel({required this.child, this.padding = const EdgeInsets.all(16), this.radius = 24, super.key});

  final Widget child;
  final EdgeInsets padding;
  final double radius;

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(radius),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 22, sigmaY: 22),
        child: DecoratedBox(
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.78),
            borderRadius: BorderRadius.circular(radius),
            border: Border.all(color: Colors.white.withOpacity(0.68)),
            boxShadow: [BoxShadow(color: AppColors.navy.withOpacity(0.08), blurRadius: 28, offset: const Offset(0, 12))],
          ),
          child: Padding(padding: padding, child: child),
        ),
      ),
    );
  }
}

class AppScrollView extends StatelessWidget {
  const AppScrollView({required this.children, this.bottomPadding = 112, super.key});

  final List<Widget> children;
  final double bottomPadding;

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: EdgeInsets.fromLTRB(20, 18 + MediaQuery.paddingOf(context).top, 20, bottomPadding + MediaQuery.paddingOf(context).bottom),
      children: children,
    );
  }
}

class Header extends StatelessWidget {
  const Header({required this.title, required this.eyebrow, this.leading, this.trailing, super.key});

  final String title;
  final String eyebrow;
  final Widget? leading;
  final Widget? trailing;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 18),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (leading != null) ...[leading!, const SizedBox(width: 12)],
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(eyebrow.toUpperCase(), style: const TextStyle(color: AppColors.muted, fontSize: 12, fontWeight: FontWeight.w900, letterSpacing: 1.8)),
                const SizedBox(height: 6),
                Text(title, style: const TextStyle(fontSize: 32, fontWeight: FontWeight.w800, height: 1.04)),
              ],
            ),
          ),
          if (trailing != null) trailing!,
        ],
      ),
    );
  }
}

class HeroCareCard extends StatelessWidget {
  const HeroCareCard({required this.onOpenAi, super.key});

  final VoidCallback onOpenAi;

  @override
  Widget build(BuildContext context) {
    return Container(
      minHeight: 176,
      padding: const EdgeInsets.all(22),
      decoration: BoxDecoration(
        color: AppColors.navy,
        borderRadius: BorderRadius.circular(28),
        gradient: const LinearGradient(colors: [AppColors.navy, AppColors.mid]),
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Text('AI-подбор', style: TextStyle(color: AppColors.accent, fontWeight: FontWeight.w800)),
                const SizedBox(height: 8),
                const Text('Соберите рутину под состояние кожи', style: TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.w800, height: 1.1)),
                const SizedBox(height: 14),
                FilledButton(onPressed: onOpenAi, child: const Text('Открыть AI')),
              ],
            ),
          ),
          const BottleScene(),
        ],
      ),
    );
  }
}

class BottleScene extends StatelessWidget {
  const BottleScene({super.key});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 100,
      height: 130,
      child: Stack(
        alignment: Alignment.center,
        children: [
          Positioned(right: 18, bottom: 8, child: _Bottle(width: 42, height: 94)),
          Positioned(left: 8, bottom: 4, child: _Bottle(width: 34, height: 70)),
          Positioned(top: 14, right: 4, child: Icon(CupertinoIcons.drop, color: AppColors.accent.withOpacity(0.75), size: 42)),
        ],
      ),
    );
  }
}

class _Bottle extends StatelessWidget {
  const _Bottle({required this.width, required this.height});

  final double width;
  final double height;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: width,
      height: height,
      decoration: BoxDecoration(
        color: AppColors.accent.withOpacity(0.9),
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: Colors.white.withOpacity(0.38)),
      ),
    );
  }
}

class StatsRow extends StatelessWidget {
  const StatsRow({required this.consultation, required this.routineDone, required this.routineTotal, super.key});

  final Consultation? consultation;
  final int routineDone;
  final int routineTotal;

  @override
  Widget build(BuildContext context) {
    final time = consultation == null ? '—' : '${consultation!.time.hour.toString().padLeft(2, '0')}:${consultation!.time.minute.toString().padLeft(2, '0')}';
    return Row(
      children: [
        const Expanded(child: StatCard(value: '0', label: 'бонусов')),
        const SizedBox(width: 10),
        Expanded(child: StatCard(value: time, label: 'консультация')),
        const SizedBox(width: 10),
        Expanded(child: StatCard(value: '$routineDone/$routineTotal', label: 'уход сегодня')),
      ],
    );
  }
}

class StatCard extends StatelessWidget {
  const StatCard({required this.value, required this.label, super.key});

  final String value;
  final String label;

  @override
  Widget build(BuildContext context) {
    return LiquidPanel(
      padding: const EdgeInsets.all(14),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(value, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w900)),
          const SizedBox(height: 4),
          Text(label, style: const TextStyle(color: AppColors.muted, fontSize: 11, fontWeight: FontWeight.w700)),
        ],
      ),
    );
  }
}

class AiQuestionCard extends StatelessWidget {
  const AiQuestionCard({required this.onTap, super.key});

  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: LiquidPanel(
        child: Row(
          children: [
            const AiMark(),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: const [
                  Text('AI-КОНСУЛЬТАНТ', style: TextStyle(color: AppColors.muted, fontSize: 11, fontWeight: FontWeight.w900, letterSpacing: 1.2)),
                  SizedBox(height: 6),
                  Text('Что беспокоит вашу кожу?', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w900)),
                  SizedBox(height: 6),
                  Text('Опишите жалобу и получите подбор средств из каталога.', style: TextStyle(color: AppColors.muted, height: 1.35)),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class AiMark extends StatelessWidget {
  const AiMark({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 52,
      height: 52,
      decoration: const BoxDecoration(color: AppColors.navy, shape: BoxShape.circle),
      child: const Icon(CupertinoIcons.sparkles, color: AppColors.accent),
    );
  }
}

class SectionTitle extends StatelessWidget {
  const SectionTitle({required this.title, this.action, this.onAction, super.key});

  final String title;
  final String? action;
  final VoidCallback? onAction;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(top: 18, bottom: 12),
      child: Row(
        children: [
          Expanded(child: Text(title, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w900))),
          if (action != null) TextButton(onPressed: onAction, child: Text(action!)),
        ],
      ),
    );
  }
}

class PromoRow extends StatelessWidget {
  const PromoRow({super.key});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: const [
        Expanded(child: PromoCard(title: '-15% на SPF', subtitle: 'при заказе с AI-рекомендацией')),
        SizedBox(width: 12),
        Expanded(child: PromoCard(title: '250 бонусов', subtitle: 'за первую консультацию')),
      ],
    );
  }
}

class PromoCard extends StatelessWidget {
  const PromoCard({required this.title, required this.subtitle, super.key});

  final String title;
  final String subtitle;

  @override
  Widget build(BuildContext context) {
    return LiquidPanel(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: const TextStyle(fontWeight: FontWeight.w900)),
          const SizedBox(height: 8),
          Text(subtitle, style: const TextStyle(color: AppColors.muted, fontSize: 12)),
        ],
      ),
    );
  }
}

class RoutineStrip extends StatelessWidget {
  const RoutineStrip({required this.done, required this.total, required this.onTap, super.key});

  final int done;
  final int total;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(top: 18),
      child: GestureDetector(
        onTap: onTap,
        child: LiquidPanel(
          child: Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('СЕГОДНЯ', style: TextStyle(color: AppColors.muted, fontSize: 11, fontWeight: FontWeight.w900, letterSpacing: 1.2)),
                    const SizedBox(height: 6),
                    const Text('Утренний уход', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w900)),
                    Text('$done из $total выполнено', style: const TextStyle(color: AppColors.muted)),
                  ],
                ),
              ),
              ProgressBubble(progress: done / total),
            ],
          ),
        ),
      ),
    );
  }
}

class SearchBox extends StatelessWidget {
  const SearchBox({required this.value, required this.onChanged, super.key});

  final String value;
  final ValueChanged<String> onChanged;

  @override
  Widget build(BuildContext context) {
    return TextField(
      onChanged: onChanged,
      decoration: InputDecoration(
        hintText: 'Поиск по уходу',
        prefixIcon: const Icon(CupertinoIcons.search),
        filled: true,
        fillColor: Colors.white,
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(22), borderSide: const BorderSide(color: AppColors.line)),
        enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(22), borderSide: const BorderSide(color: AppColors.line)),
      ),
    );
  }
}

class ProductGrid extends StatelessWidget {
  const ProductGrid({
    required this.products,
    required this.favoriteIds,
    required this.onFavorite,
    required this.onAdd,
    required this.onProduct,
    super.key,
  });

  final List<Product> products;
  final Set<int> favoriteIds;
  final ValueChanged<Product> onFavorite;
  final ValueChanged<Product> onAdd;
  final ValueChanged<Product> onProduct;

  @override
  Widget build(BuildContext context) {
    return GridView.builder(
      itemCount: products.length,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(crossAxisCount: 2, mainAxisSpacing: 14, crossAxisSpacing: 14, childAspectRatio: 0.57),
      itemBuilder: (context, index) {
        final product = products[index];
        return ProductCard(
          product: product,
          favorite: favoriteIds.contains(product.id),
          onFavorite: () => onFavorite(product),
          onAdd: () => onAdd(product),
          onTap: () => onProduct(product),
        );
      },
    );
  }
}

class ProductCard extends StatelessWidget {
  const ProductCard({
    required this.product,
    required this.favorite,
    required this.onFavorite,
    required this.onAdd,
    required this.onTap,
    super.key,
  });

  final Product product;
  final bool favorite;
  final VoidCallback onFavorite;
  final VoidCallback onAdd;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Container(
      clipBehavior: Clip.antiAlias,
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(22),
        border: Border.all(color: AppColors.line),
        boxShadow: [BoxShadow(color: AppColors.navy.withOpacity(0.06), blurRadius: 22, offset: const Offset(0, 8))],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Expanded(
            flex: 8,
            child: GestureDetector(
              onTap: onTap,
              child: ProductVisual(
                favorite: favorite,
                onFavorite: onFavorite,
              ),
            ),
          ),
          Expanded(
            flex: 11,
            child: Padding(
              padding: const EdgeInsets.all(14),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(product.brand.toUpperCase(), maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(color: AppColors.muted, fontSize: 11, fontWeight: FontWeight.w900, letterSpacing: 1.4)),
                  const SizedBox(height: 6),
                  GestureDetector(
                    onTap: onTap,
                    child: Text(product.name, maxLines: 2, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 16, height: 1.08, fontWeight: FontWeight.w900)),
                  ),
                  const SizedBox(height: 8),
                  Text('★★★★★ ${product.rating}', style: const TextStyle(color: Color(0xFFF59A12), fontSize: 13, fontWeight: FontWeight.w800)),
                  const SizedBox(height: 6),
                  Text('${formatMoney(product.price)} сом', style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w900)),
                  const Spacer(),
                  SizedBox(width: double.infinity, child: FilledButton(onPressed: onAdd, child: const Text('+ В корзину'))),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class ProductVisual extends StatelessWidget {
  const ProductVisual({required this.favorite, required this.onFavorite, super.key});

  final bool favorite;
  final VoidCallback onFavorite;

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        Positioned.fill(
          child: DecoratedBox(
            decoration: const BoxDecoration(gradient: LinearGradient(colors: [AppColors.soft, AppColors.accent])),
            child: Center(child: Icon(CupertinoIcons.drop, size: 58, color: AppColors.mid.withOpacity(0.26))),
          ),
        ),
        Positioned(
          top: 12,
          right: 12,
          child: GestureDetector(
            onTap: onFavorite,
            child: Container(
              width: 42,
              height: 42,
              decoration: const BoxDecoration(color: Colors.white, shape: BoxShape.circle),
              child: Icon(favorite ? CupertinoIcons.heart_fill : CupertinoIcons.heart, color: favorite ? AppColors.mid : AppColors.muted),
            ),
          ),
        ),
      ],
    );
  }
}

class ProductSheet extends StatelessWidget {
  const ProductSheet({required this.product, required this.onAdd, super.key});

  final Product product;
  final VoidCallback onAdd;

  @override
  Widget build(BuildContext context) {
    return Container(
      constraints: BoxConstraints(maxHeight: MediaQuery.sizeOf(context).height * 0.9),
      decoration: const BoxDecoration(color: Colors.white, borderRadius: BorderRadius.vertical(top: Radius.circular(34))),
      child: ListView(
        padding: EdgeInsets.fromLTRB(24, 0, 24, 24 + MediaQuery.paddingOf(context).bottom),
        children: [
          const SizedBox(height: 230, child: Center(child: Icon(CupertinoIcons.drop, size: 92, color: AppColors.accent))),
          Text(product.brand.toUpperCase(), style: const TextStyle(color: Color(0xFF4283FF), fontSize: 14, fontWeight: FontWeight.w900, letterSpacing: 1.5)),
          const SizedBox(height: 10),
          Text(product.name, style: const TextStyle(fontSize: 34, height: 1.1, fontWeight: FontWeight.w900)),
          const SizedBox(height: 14),
          Row(children: [Text('${formatMoney(product.price)} сом', style: const TextStyle(fontSize: 32, fontWeight: FontWeight.w900)), const SizedBox(width: 12), const Text('★★★★★ 4.9', style: TextStyle(color: Color(0xFFF59A12), fontWeight: FontWeight.w800))]),
          const SizedBox(height: 18),
          const Wrap(spacing: 8, runSpacing: 8, children: [Tag('Жирная кожа'), Tag('Акне'), Tag('Комбинированная')]),
          const SizedBox(height: 24),
          const SectionCaption('О продукте'),
          Text(product.description, style: const TextStyle(color: Color(0xFF5F6A7D), fontSize: 18, height: 1.42)),
          const SizedBox(height: 22),
          const SectionCaption('Способ применения'),
          Text(product.usage, style: const TextStyle(color: Color(0xFF5F6A7D), fontSize: 18, height: 1.42)),
          const SizedBox(height: 28),
          FilledButton(onPressed: onAdd, child: Text('Добавить в корзину · ${formatMoney(product.price)} сом')),
        ],
      ),
    );
  }
}

class Tag extends StatelessWidget {
  const Tag(this.text, {super.key});

  final String text;

  @override
  Widget build(BuildContext context) {
    return DecoratedBox(
      decoration: BoxDecoration(color: AppColors.soft, borderRadius: BorderRadius.circular(999)),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 7),
        child: Text(text, style: const TextStyle(color: AppColors.mid, fontWeight: FontWeight.w800)),
      ),
    );
  }
}

class ChatBubble extends StatelessWidget {
  const ChatBubble.ai({required this.text, super.key})
      : products = const [],
        onAdd = null,
        isUser = false;

  const ChatBubble.user({required this.text, super.key})
      : products = const [],
        onAdd = null,
        isUser = true;

  const ChatBubble.aiRecommendation({required this.products, required this.onAdd, super.key})
      : text = 'Я проанализировала запрос. Рекомендую начать с этих средств:',
        isUser = false;

  final String text;
  final bool isUser;
  final List<Product> products;
  final ValueChanged<Product>? onAdd;

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        constraints: BoxConstraints(maxWidth: MediaQuery.sizeOf(context).width * 0.82),
        margin: const EdgeInsets.only(bottom: 10),
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: isUser ? AppColors.mid : Colors.white,
          borderRadius: BorderRadius.circular(22).copyWith(bottomLeft: Radius.circular(isUser ? 22 : 8), bottomRight: Radius.circular(isUser ? 8 : 22)),
          boxShadow: [BoxShadow(color: AppColors.navy.withOpacity(0.06), blurRadius: 22, offset: const Offset(0, 8))],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(text, style: TextStyle(color: isUser ? Colors.white : AppColors.navy, fontWeight: FontWeight.w700, height: 1.42)),
            ...products.map((product) => ChatRecoCard(product: product, onAdd: () => onAdd?.call(product))),
          ],
        ),
      ),
    );
  }
}

class ChatRecoCard extends StatelessWidget {
  const ChatRecoCard({required this.product, required this.onAdd, super.key});

  final Product product;
  final VoidCallback onAdd;

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(top: 10),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(color: AppColors.soft, borderRadius: BorderRadius.circular(18)),
      child: Row(
        children: [
          Container(width: 56, height: 56, decoration: BoxDecoration(color: AppColors.accent.withOpacity(0.45), borderRadius: BorderRadius.circular(16)), child: const Icon(CupertinoIcons.drop, color: AppColors.mid)),
          const SizedBox(width: 12),
          Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text(product.name, style: const TextStyle(fontWeight: FontWeight.w900)), Text('ID ${product.id} · ${formatMoney(product.price)} сом', style: const TextStyle(color: AppColors.muted, fontWeight: FontWeight.w700)), TextButton(onPressed: onAdd, child: const Text('Добавить в корзину →'))])),
        ],
      ),
    );
  }
}

class AiHero extends StatelessWidget {
  const AiHero({super.key});

  @override
  Widget build(BuildContext context) {
    return LiquidPanel(
      child: Row(
        children: const [
          AiMark(),
          SizedBox(width: 14),
          Expanded(child: Text('AI анализирует skin card, историю заказов и каталог, чтобы предложить понятную рутину.', style: TextStyle(color: AppColors.muted, height: 1.4))),
        ],
      ),
    );
  }
}

class RoutineHero extends StatelessWidget {
  const RoutineHero({required this.done, required this.total, super.key});

  final int done;
  final int total;

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 18),
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(color: AppColors.navy, borderRadius: BorderRadius.circular(28)),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('Мой уход', style: TextStyle(color: Colors.white, fontSize: 34, fontWeight: FontWeight.w700)),
                Text(DateTime.now().toLocal().toString().split(' ').first, style: const TextStyle(color: AppColors.muted, fontSize: 16, fontWeight: FontWeight.w800)),
                const SizedBox(height: 20),
                const Text('Прогресс сегодня', style: TextStyle(color: AppColors.muted, fontWeight: FontWeight.w700)),
                Text('$done из $total', style: const TextStyle(color: AppColors.accent, fontSize: 18, fontWeight: FontWeight.w900)),
              ],
            ),
          ),
          ProgressBubble(progress: done / total, large: true),
        ],
      ),
    );
  }
}

class ProgressBubble extends StatelessWidget {
  const ProgressBubble({required this.progress, this.large = false, super.key});

  final double progress;
  final bool large;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: large ? 76 : 58,
      height: large ? 76 : 58,
      child: Stack(
        fit: StackFit.expand,
        children: [
          CircularProgressIndicator(value: progress, strokeWidth: large ? 7 : 5, backgroundColor: AppColors.soft, color: AppColors.accent),
          Center(child: Text('${(progress * 100).round()}%', style: TextStyle(color: large ? Colors.white : AppColors.navy, fontSize: large ? 16 : 12, fontWeight: FontWeight.w900))),
        ],
      ),
    );
  }
}

class RoutineGroup extends StatelessWidget {
  const RoutineGroup({required this.title, required this.icon, required this.steps, required this.done, required this.onToggle, super.key});

  final String title;
  final IconData icon;
  final List<String> steps;
  final Set<String> done;
  final ValueChanged<String> onToggle;

  @override
  Widget build(BuildContext context) {
    final doneCount = steps.where(done.contains).length;
    return Padding(
      padding: const EdgeInsets.only(bottom: 14),
      child: LiquidPanel(
        padding: EdgeInsets.zero,
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.all(16),
              child: Row(children: [Icon(icon, color: AppColors.mid), const SizedBox(width: 12), Expanded(child: Text(title, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w900))), Text('$doneCount/${steps.length} выполнено', style: const TextStyle(color: AppColors.muted, fontWeight: FontWeight.w800))]),
            ),
            ...steps.map((step) {
              final isDone = done.contains(step);
              return ListTile(
                onTap: () => onToggle(step),
                leading: CircleAvatar(backgroundColor: isDone ? AppColors.navy : Colors.white, child: Icon(isDone ? CupertinoIcons.check_mark : CupertinoIcons.circle, color: isDone ? Colors.white : AppColors.muted)),
                title: Text(step, style: TextStyle(fontWeight: FontWeight.w800, decoration: isDone ? TextDecoration.lineThrough : null, color: isDone ? AppColors.muted : null)),
                trailing: const Text('2 мин', style: TextStyle(color: AppColors.muted, fontWeight: FontWeight.w800)),
              );
            }),
          ],
        ),
      ),
    );
  }
}

class ConsultationTile extends StatelessWidget {
  const ConsultationTile({required this.item, super.key});

  final Consultation item;

  @override
  Widget build(BuildContext context) {
    return LiquidPanel(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('${item.time.day}.${item.time.month}.${item.time.year} ${item.time.hour.toString().padLeft(2, '0')}:${item.time.minute.toString().padLeft(2, '0')}', style: const TextStyle(fontWeight: FontWeight.w900)),
          const SizedBox(height: 6),
          Text('Консультант: ${item.specialist}', style: const TextStyle(color: AppColors.muted)),
          Text('Жалоба: ${item.concern}', style: const TextStyle(color: AppColors.muted)),
        ],
      ),
    );
  }
}

class ProfileHeader extends StatelessWidget {
  const ProfileHeader({super.key});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        const CircleAvatar(radius: 31, backgroundColor: AppColors.navy, child: Text('D', style: TextStyle(color: AppColors.accent, fontSize: 24, fontWeight: FontWeight.w900))),
        const SizedBox(width: 14),
        Column(crossAxisAlignment: CrossAxisAlignment.start, children: const [Text('ПРОФИЛЬ', style: TextStyle(color: AppColors.muted, fontSize: 12, fontWeight: FontWeight.w900, letterSpacing: 1.5)), SizedBox(height: 4), Text('Клиент', style: TextStyle(fontSize: 30, fontWeight: FontWeight.w900)), Text('+996', style: TextStyle(color: AppColors.muted))]),
      ],
    );
  }
}

class ProfileForm extends StatelessWidget {
  const ProfileForm({super.key});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(top: 18),
      child: LiquidPanel(
        child: Column(
          children: const [
            TextField(decoration: InputDecoration(labelText: 'Имя', border: OutlineInputBorder())),
            SizedBox(height: 12),
            TextField(decoration: InputDecoration(labelText: 'Тип кожи', border: OutlineInputBorder())),
            SizedBox(height: 12),
            TextField(maxLines: 3, decoration: InputDecoration(labelText: 'Особенности', border: OutlineInputBorder())),
          ],
        ),
      ),
    );
  }
}

class BonusCard extends StatelessWidget {
  const BonusCard({super.key});

  @override
  Widget build(BuildContext context) {
    return const Padding(
      padding: EdgeInsets.only(top: 14),
      child: LiquidPanel(
        child: Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [Text('Бонусный баланс', style: TextStyle(color: AppColors.muted, fontWeight: FontWeight.w800)), Text('0 сом', style: TextStyle(fontSize: 22, fontWeight: FontWeight.w900))]),
      ),
    );
  }
}

class ProfileLink extends StatelessWidget {
  const ProfileLink({required this.title, required this.value, required this.onTap, super.key});

  final String title;
  final String value;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(top: 14),
      child: LiquidPanel(
        child: ListTile(
          contentPadding: EdgeInsets.zero,
          title: Text(title, style: const TextStyle(fontWeight: FontWeight.w900)),
          subtitle: Text(value),
          trailing: const Icon(CupertinoIcons.chevron_right),
          onTap: onTap,
        ),
      ),
    );
  }
}

class CardBindingPanel extends StatelessWidget {
  const CardBindingPanel({super.key});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(top: 14),
      child: Container(
        padding: const EdgeInsets.all(18),
        decoration: BoxDecoration(color: AppColors.navy, borderRadius: BorderRadius.circular(24), gradient: const LinearGradient(colors: [AppColors.navy, AppColors.mid])),
        child: Row(
          children: [
            const Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text('•••• 2026', style: TextStyle(color: AppColors.accent)), SizedBox(height: 6), Text('Локальная карта', style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.w900))])),
            OutlinedButton(onPressed: () {}, child: const Text('Привязать')),
          ],
        ),
      ),
    );
  }
}

class CartTile extends StatelessWidget {
  const CartTile({required this.line, required this.onInc, required this.onDec, required this.onRemove, super.key});

  final CartLine line;
  final VoidCallback onInc;
  final VoidCallback onDec;
  final VoidCallback onRemove;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: LiquidPanel(
        child: Row(
          children: [
            Expanded(
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text(line.product.name, style: const TextStyle(fontWeight: FontWeight.w900)), Text('${formatMoney(line.product.price)} сом · ${line.quantity} шт', style: const TextStyle(color: AppColors.muted)), TextButton(onPressed: onRemove, child: const Text('Убрать'))]),
            ),
            Row(children: [IconButton(onPressed: onDec, icon: const Icon(CupertinoIcons.minus)), Text('${line.quantity}', style: const TextStyle(fontWeight: FontWeight.w900)), IconButton(onPressed: onInc, icon: const Icon(CupertinoIcons.plus))]),
          ],
        ),
      ),
    );
  }
}

class CheckoutFields extends StatelessWidget {
  const CheckoutFields({super.key});

  @override
  Widget build(BuildContext context) {
    return LiquidPanel(
      child: Column(
        children: const [
          TextField(decoration: InputDecoration(labelText: 'Адрес доставки', hintText: 'Бишкек, улица, дом, квартира', border: OutlineInputBorder())),
          SizedBox(height: 12),
          TextField(decoration: InputDecoration(labelText: 'Карта', hintText: 'Локальная карта •••• 2026', border: OutlineInputBorder())),
        ],
      ),
    );
  }
}

class BadgeIconButton extends StatelessWidget {
  const BadgeIconButton({required this.icon, required this.count, required this.onTap, super.key});

  final IconData icon;
  final int count;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Stack(
      clipBehavior: Clip.none,
      children: [
        LiquidPanel(padding: EdgeInsets.zero, radius: 16, child: SizedBox(width: 44, height: 44, child: IconButton(onPressed: onTap, icon: Icon(icon, color: AppColors.navy)))),
        if (count > 0)
          Positioned(
            top: -5,
            right: -5,
            child: Container(
              minWidth: 18,
              height: 18,
              alignment: Alignment.center,
              decoration: const BoxDecoration(color: AppColors.navy, shape: BoxShape.circle),
              child: Text('$count', style: const TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.w900)),
            ),
          ),
      ],
    );
  }
}

class BackButtonGlass extends StatelessWidget {
  const BackButtonGlass({required this.onTap, super.key});

  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return LiquidPanel(padding: EdgeInsets.zero, radius: 16, child: SizedBox(width: 44, height: 44, child: IconButton(onPressed: onTap, icon: const Icon(CupertinoIcons.chevron_left, color: AppColors.navy))));
  }
}

class EmptyPanel extends StatelessWidget {
  const EmptyPanel({required this.title, required this.text, super.key});

  final String title;
  final String text;

  @override
  Widget build(BuildContext context) {
    return LiquidPanel(
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text(title, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w900)), const SizedBox(height: 6), Text(text, style: const TextStyle(color: AppColors.muted))]),
    );
  }
}

class SimpleHistoryScreen extends StatelessWidget {
  const SimpleHistoryScreen({required this.title, required this.empty, super.key});

  final String title;
  final String empty;

  @override
  Widget build(BuildContext context) {
    return Scaffold(body: AppScrollView(children: [Header(title: title, eyebrow: 'Профиль', leading: BackButtonGlass(onTap: () => Navigator.pop(context))), EmptyPanel(title: empty, text: 'История появится после синхронизации с backend.')]));
  }
}

class ConsultationHistoryScreen extends StatelessWidget {
  const ConsultationHistoryScreen({required this.consultations, super.key});

  final List<Consultation> consultations;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: AppScrollView(
        children: [
          Header(title: 'История консультаций', eyebrow: 'Профиль', leading: BackButtonGlass(onTap: () => Navigator.pop(context))),
          if (consultations.isEmpty)
            const EmptyPanel(title: 'Истории нет', text: 'Запишитесь на первую консультацию.')
          else
            ...consultations.map((item) => Padding(padding: const EdgeInsets.only(bottom: 12), child: ConsultationTile(item: item))),
        ],
      ),
    );
  }
}

class SectionCaption extends StatelessWidget {
  const SectionCaption(this.text, {super.key});

  final String text;

  @override
  Widget build(BuildContext context) {
    return Text(text.toUpperCase(), style: const TextStyle(color: AppColors.muted, fontSize: 15, fontWeight: FontWeight.w900, letterSpacing: 1.7));
  }
}

String formatMoney(int value) {
  return value.toString().replaceAllMapped(RegExp(r'\B(?=(\d{3})+(?!\d))'), (match) => ' ');
}
