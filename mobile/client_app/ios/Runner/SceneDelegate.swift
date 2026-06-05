import SwiftUI
import UIKit

final class SceneDelegate: UIResponder, UIWindowSceneDelegate {
    var window: UIWindow?

    func scene(
        _ scene: UIScene,
        willConnectTo session: UISceneSession,
        options connectionOptions: UIScene.ConnectionOptions
    ) {
        guard let windowScene = scene as? UIWindowScene else { return }

        let window = UIWindow(windowScene: windowScene)
        window.rootViewController = UIHostingController(rootView: DemiResultsGlassApp())
        self.window = window
        window.makeKeyAndVisible()
    }
}

private struct DemiResultsGlassApp: View {
    @State private var selectedTab = 0
    @State private var cartCount = 1
    @State private var favoriteIDs: Set<Int> = [1]
    @State private var selectedCategory = "Все"

    private let products = DemoProduct.samples
    private let categories = ["Все", "Увлажнение", "SPF", "Сыворотки", "Очищение"]

    var body: some View {
        ZStack(alignment: .bottom) {
            Color(red: 0.965, green: 0.976, blue: 0.984)
                .ignoresSafeArea()

            ScrollView(showsIndicators: false) {
                VStack(alignment: .leading, spacing: 18) {
                    header

                    switch selectedTab {
                    case 0:
                        home
                    case 1:
                        catalog
                    case 2:
                        aiChat
                    case 3:
                        routine
                    default:
                        profile
                    }
                }
                .padding(.horizontal, 20)
                .padding(.top, 20)
                .padding(.bottom, 118)
            }

            nativeLiquidGlassNav
                .padding(.horizontal, 20)
                .padding(.bottom, 12)
        }
        .tint(.demiNavy)
    }

    private var header: some View {
        HStack(alignment: .top) {
            VStack(alignment: .leading, spacing: 6) {
                Text(selectedTab == 1 ? "КАТАЛОГ" : "DEMIRESULTS")
                    .font(.system(size: 12, weight: .heavy))
                    .foregroundStyle(.demiMuted)
                    .tracking(2)

                Text(headerTitle)
                    .font(.system(size: selectedTab == 0 ? 38 : 34, weight: .heavy))
                    .foregroundStyle(.demiNavy)
                    .lineLimit(3)
            }

            Spacer()

            if selectedTab == 1 {
                HStack(spacing: 8) {
                    glassIcon(systemName: "heart", badge: favoriteIDs.count)
                    glassIcon(systemName: "bag", badge: cartCount)
                }
            } else {
                glassIcon(systemName: "arrow.clockwise", badge: 0)
            }
        }
    }

    private var headerTitle: String {
        switch selectedTab {
        case 0: "Ваш персональный уход"
        case 1: "Средства"
        case 2: "AI-консультант"
        case 3: "Мой уход"
        default: "Профиль"
        }
    }

    private var home: some View {
        VStack(alignment: .leading, spacing: 18) {
            heroCard
            stats
            aiQuestionCard

            HStack {
                Text("Популярное")
                    .font(.system(size: 28, weight: .heavy))
                Spacer()
                Button("Все") { selectedTab = 1 }
                    .font(.system(size: 18, weight: .bold))
            }

            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 14) {
                    ForEach(products.prefix(4)) { product in
                        ProductGlassCard(
                            product: product,
                            isFavorite: favoriteIDs.contains(product.id),
                            onFavorite: { toggleFavorite(product) },
                            onCart: { cartCount += 1 }
                        )
                        .frame(width: 190, height: 340)
                    }
                }
            }

            promoRow
        }
    }

    private var heroCard: some View {
        HStack {
            VStack(alignment: .leading, spacing: 14) {
                Text("AI-подбор")
                    .font(.system(size: 16, weight: .heavy))
                    .foregroundStyle(.demiAccent)

                Text("Соберите рутину под состояние кожи")
                    .font(.system(size: 28, weight: .heavy))
                    .foregroundStyle(.white)
                    .lineLimit(4)
                    .minimumScaleFactor(0.82)

                Button("Открыть AI") { selectedTab = 2 }
                    .font(.system(size: 18, weight: .bold))
                    .foregroundStyle(.white)
                    .padding(.horizontal, 24)
                    .padding(.vertical, 12)
                    .background(.white.opacity(0.14), in: Capsule())
            }

            Spacer()

            Image(systemName: "drop")
                .font(.system(size: 74, weight: .light))
                .foregroundStyle(.demiAccent.opacity(0.72))
        }
        .padding(24)
        .frame(minHeight: 230)
        .background(
            LinearGradient(colors: [.demiNavy, .demiMid], startPoint: .topLeading, endPoint: .bottomTrailing),
            in: RoundedRectangle(cornerRadius: 30, style: .continuous)
        )
    }

    private var stats: some View {
        HStack(spacing: 12) {
            stat("0", "бонусов")
            stat("14:30", "консульт.")
            stat("3/8", "уход сегодня")
        }
    }

    private func stat(_ value: String, _ label: String) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(value)
                .font(.system(size: value.count > 3 ? 23 : 28, weight: .heavy))
                .foregroundStyle(.demiNavy)
                .lineLimit(1)
                .minimumScaleFactor(0.72)
            Text(label)
                .font(.system(size: 13, weight: .heavy))
                .foregroundStyle(.demiMuted)
                .lineLimit(2)
                .minimumScaleFactor(0.82)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(18)
        .nativeGlass(cornerRadius: 24)
    }

    private var aiQuestionCard: some View {
        HStack(spacing: 18) {
            Circle()
                .fill(.demiNavy)
                .frame(width: 58, height: 58)
                .overlay(Image(systemName: "sparkles").foregroundStyle(.demiAccent))

            VStack(alignment: .leading, spacing: 7) {
                Text("AI-КОНСУЛЬТАНТ")
                    .font(.system(size: 13, weight: .heavy))
                    .foregroundStyle(.demiMuted)
                    .tracking(1.5)
                Text("Что беспокоит вашу кожу?")
                    .font(.system(size: 25, weight: .heavy))
                    .foregroundStyle(.demiNavy)
                Text("Опишите жалобу и получите подбор средств из каталога.")
                    .font(.system(size: 16, weight: .medium))
                    .foregroundStyle(.demiMuted)
            }
        }
        .padding(20)
        .nativeGlass(cornerRadius: 28)
        .onTapGesture { selectedTab = 2 }
    }

    private var promoRow: some View {
        HStack(spacing: 12) {
            promo("-15% на SPF", "при заказе с AI-рекомендацией")
            promo("250 бонусов", "за первую консультацию")
        }
    }

    private func promo(_ title: String, _ subtitle: String) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title).font(.system(size: 17, weight: .heavy))
            Text(subtitle).font(.system(size: 13, weight: .semibold)).foregroundStyle(.demiMuted)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(16)
        .nativeGlass(cornerRadius: 24)
    }

    private var catalog: some View {
        VStack(alignment: .leading, spacing: 16) {
            HStack {
                Image(systemName: "magnifyingglass")
                Text("Поиск по уходу")
                    .foregroundStyle(.demiMuted)
                Spacer()
            }
            .padding(18)
            .nativeGlass(cornerRadius: 22)

            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 8) {
                    ForEach(categories, id: \.self) { category in
                        Button(category) { selectedCategory = category }
                            .font(.system(size: 16, weight: .bold))
                            .padding(.horizontal, 18)
                            .padding(.vertical, 10)
                            .foregroundStyle(selectedCategory == category ? .white : .demiMid)
                            .background(selectedCategory == category ? .demiNavy : .white.opacity(0.72), in: Capsule())
                            .nativeGlassIfAvailable(cornerRadius: 999)
                    }
                }
            }

            LazyVGrid(columns: [GridItem(.flexible(), spacing: 14), GridItem(.flexible(), spacing: 14)], spacing: 14) {
                ForEach(filteredProducts) { product in
                    ProductGlassCard(
                        product: product,
                        isFavorite: favoriteIDs.contains(product.id),
                        onFavorite: { toggleFavorite(product) },
                        onCart: { cartCount += 1 }
                    )
                    .frame(height: 340)
                }
            }
        }
    }

    private var filteredProducts: [DemoProduct] {
        selectedCategory == "Все" ? products : products.filter { $0.category == selectedCategory }
    }

    private var aiChat: some View {
        VStack(alignment: .leading, spacing: 16) {
            chatBubble("Расскажите, что сейчас беспокоит кожу: сухость, высыпания, пигментация или чувствительность?", isUser: false)
            chatBubble("Хочу мягкий уход и SPF на каждый день.", isUser: true)
            VStack(alignment: .leading, spacing: 12) {
                Text("Я проанализировала запрос. Рекомендую начать с этих средств:")
                    .font(.system(size: 18, weight: .bold))
                reco(products[0])
                reco(products[3])
            }
            .padding(16)
            .nativeGlass(cornerRadius: 24)

            HStack {
                Text("Напишите вопрос...")
                    .foregroundStyle(.demiMuted)
                Spacer()
                Image(systemName: "arrow.up")
                    .font(.system(size: 18, weight: .heavy))
                    .foregroundStyle(.demiNavy)
                    .padding(13)
                    .background(.demiAccent, in: Circle())
            }
            .padding(12)
            .nativeGlass(cornerRadius: 26)
        }
    }

    private func chatBubble(_ text: String, isUser: Bool) -> some View {
        Text(text)
            .font(.system(size: 18, weight: .bold))
            .foregroundStyle(isUser ? .white : .demiNavy)
            .padding(16)
            .frame(maxWidth: 310, alignment: .leading)
            .background(isUser ? .demiMid : .white.opacity(0.78), in: RoundedRectangle(cornerRadius: 22, style: .continuous))
            .frame(maxWidth: .infinity, alignment: isUser ? .trailing : .leading)
    }

    private func reco(_ product: DemoProduct) -> some View {
        HStack(spacing: 12) {
            RoundedRectangle(cornerRadius: 16)
                .fill(.demiAccent.opacity(0.35))
                .frame(width: 58, height: 58)
                .overlay(Image(systemName: "drop").foregroundStyle(.demiMid))
            VStack(alignment: .leading, spacing: 4) {
                Text(product.name).font(.system(size: 16, weight: .heavy))
                Text("ID \(product.id) · \(product.price) сом")
                    .font(.system(size: 14, weight: .bold))
                    .foregroundStyle(.demiMuted)
                Button("Добавить в корзину →") { cartCount += 1 }
                    .font(.system(size: 15, weight: .heavy))
            }
        }
        .padding(12)
        .background(.demiSoft, in: RoundedRectangle(cornerRadius: 18, style: .continuous))
    }

    private var routine: some View {
        VStack(spacing: 14) {
            VStack(alignment: .leading, spacing: 12) {
                Text("Мой уход")
                    .font(.system(size: 38, weight: .bold))
                    .foregroundStyle(.white)
                Text("Прогресс сегодня")
                    .font(.system(size: 18, weight: .bold))
                    .foregroundStyle(.demiMuted)
                ProgressView(value: 3, total: 8)
                    .tint(.demiAccent)
            }
            .padding(24)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(.demiNavy, in: RoundedRectangle(cornerRadius: 30, style: .continuous))

            routineGroup("Утренний уход", steps: ["Умывание", "Тонер", "Увлажняющий крем", "SPF защита"], done: 2)
            routineGroup("Вечерний уход", steps: ["Двойное очищение", "Сыворотка", "Ночной крем"], done: 1)
        }
    }

    private func routineGroup(_ title: String, steps: [String], done: Int) -> some View {
        VStack(alignment: .leading, spacing: 0) {
            HStack {
                Text(title).font(.system(size: 20, weight: .heavy))
                Spacer()
                Text("\(done)/\(steps.count) выполнено")
                    .font(.system(size: 14, weight: .heavy))
                    .foregroundStyle(.demiMuted)
            }
            .padding(18)

            ForEach(Array(steps.enumerated()), id: \.offset) { index, step in
                HStack {
                    Image(systemName: index < done ? "checkmark.circle.fill" : "circle")
                        .foregroundStyle(index < done ? .demiNavy : .demiMuted)
                    Text(step)
                        .font(.system(size: 18, weight: .bold))
                        .strikethrough(index < done)
                    Spacer()
                    Text("2 мин").foregroundStyle(.demiMuted)
                }
                .padding(18)
            }
        }
        .nativeGlass(cornerRadius: 26)
    }

    private var profile: some View {
        VStack(alignment: .leading, spacing: 14) {
            HStack(spacing: 14) {
                Circle()
                    .fill(.demiNavy)
                    .frame(width: 64, height: 64)
                    .overlay(Text("D").font(.system(size: 28, weight: .heavy)).foregroundStyle(.demiAccent))
                VStack(alignment: .leading) {
                    Text("Клиент").font(.system(size: 32, weight: .heavy))
                    Text("+996").foregroundStyle(.demiMuted)
                }
            }
            profileLink("История заказов", "0 заказов")
            profileLink("История консультаций", "1 запись")
            VStack(alignment: .leading, spacing: 14) {
                Text("НАСТРОЙКИ ТЕМЫ")
                    .font(.system(size: 13, weight: .heavy))
                    .foregroundStyle(.demiMuted)
                    .tracking(1.5)
                HStack {
                    Button("Светлая") {}
                        .padding()
                        .frame(maxWidth: .infinity)
                        .nativeGlass(cornerRadius: 16)
                    Button("Тёмная") {}
                        .padding()
                        .frame(maxWidth: .infinity)
                        .nativeGlass(cornerRadius: 16)
                }
            }
            .padding(18)
            .nativeGlass(cornerRadius: 24)
        }
    }

    private func profileLink(_ title: String, _ value: String) -> some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text(title).font(.system(size: 18, weight: .heavy))
                Text(value).foregroundStyle(.demiMuted)
            }
            Spacer()
            Image(systemName: "chevron.right")
        }
        .padding(18)
        .nativeGlass(cornerRadius: 24)
    }

    private var nativeLiquidGlassNav: some View {
        GlassCompatContainer {
            HStack(spacing: 8) {
                navButton(0, "house", "Главная")
                navButton(1, "square.grid.2x2", "Каталог")
                navButton(2, "sparkles", "AI", prominent: true)
                navButton(3, "circle.grid.hex", "Уход")
                navButton(4, "person.circle", "Профиль")
            }
            .padding(8)
            .nativeGlass(cornerRadius: 30)
        }
    }

    private func navButton(_ index: Int, _ systemName: String, _ title: String, prominent: Bool = false) -> some View {
        Button {
            withAnimation(.spring(response: 0.45, dampingFraction: 0.82)) {
                selectedTab = index
            }
        } label: {
            VStack(spacing: 4) {
                Image(systemName: systemName)
                    .font(.system(size: prominent ? 18 : 20, weight: .bold))
                    .frame(width: prominent ? 36 : 30, height: prominent ? 36 : 30)
                    .foregroundStyle(prominent ? .demiAccent : (selectedTab == index ? .demiNavy : .demiMuted))
                    .background(prominent ? .demiNavy : .clear, in: RoundedRectangle(cornerRadius: 14, style: .continuous))
                Text(title)
                    .font(.system(size: 11, weight: .heavy))
                    .foregroundStyle(selectedTab == index ? .demiNavy : .demiMuted)
            }
            .frame(maxWidth: .infinity)
            .frame(height: 58)
            .background(selectedTab == index ? .demiAccent.opacity(0.52) : .clear, in: RoundedRectangle(cornerRadius: 22, style: .continuous))
        }
        .buttonStyle(.plain)
        .nativeGlassIfAvailable(cornerRadius: 22)
    }

    private func glassIcon(systemName: String, badge: Int) -> some View {
        ZStack(alignment: .topTrailing) {
            Image(systemName: systemName)
                .font(.system(size: 20, weight: .bold))
                .foregroundStyle(.demiNavy)
                .frame(width: 46, height: 46)
                .nativeGlass(cornerRadius: 16)
            if badge > 0 {
                Text("\(badge)")
                    .font(.system(size: 10, weight: .heavy))
                    .foregroundStyle(.white)
                    .frame(minWidth: 18, minHeight: 18)
                    .background(.demiNavy, in: Circle())
                    .offset(x: 5, y: -5)
            }
        }
    }

    private func toggleFavorite(_ product: DemoProduct) {
        if favoriteIDs.contains(product.id) {
            favoriteIDs.remove(product.id)
        } else {
            favoriteIDs.insert(product.id)
        }
    }
}

private struct ProductGlassCard: View {
    let product: DemoProduct
    let isFavorite: Bool
    let onFavorite: () -> Void
    let onCart: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            ZStack(alignment: .topTrailing) {
                Rectangle()
                    .fill(LinearGradient(colors: [.demiSoft, .demiAccent], startPoint: .topLeading, endPoint: .bottomTrailing))
                    .overlay(Image(systemName: "drop").font(.system(size: 58)).foregroundStyle(.demiMid.opacity(0.25)))
                Button(action: onFavorite) {
                    Image(systemName: isFavorite ? "heart.fill" : "heart")
                        .foregroundStyle(isFavorite ? .demiMid : .demiMuted)
                        .frame(width: 42, height: 42)
                        .background(.white.opacity(0.9), in: Circle())
                }
                .padding(12)
            }
            .frame(height: 132)

            VStack(alignment: .leading, spacing: 8) {
                Text(product.brand.uppercased())
                    .font(.system(size: 11, weight: .heavy))
                    .foregroundStyle(.demiMuted)
                    .tracking(1.3)
                    .lineLimit(1)
                Text(product.name)
                    .font(.system(size: 16, weight: .heavy))
                    .foregroundStyle(.demiNavy)
                    .lineLimit(2)
                Text("★★★★★ 4.9")
                    .font(.system(size: 13, weight: .bold))
                    .foregroundStyle(.orange)
                Text("\(product.price) сом")
                    .font(.system(size: 19, weight: .heavy))
                    .foregroundStyle(.demiNavy)
                Spacer()
                Button("+ В корзину", action: onCart)
                    .font(.system(size: 15, weight: .heavy))
                    .foregroundStyle(.white)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 11)
                    .background(.demiNavy, in: RoundedRectangle(cornerRadius: 16, style: .continuous))
            }
            .padding(14)
        }
        .background(.white.opacity(0.82), in: RoundedRectangle(cornerRadius: 24, style: .continuous))
        .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))
        .nativeGlassIfAvailable(cornerRadius: 24)
    }
}

private struct DemoProduct: Identifiable {
    let id: Int
    let brand: String
    let name: String
    let category: String
    let price: Int

    static let samples = [
        DemoProduct(id: 1, brand: "DemiLab", name: "Gentle Cleansing Gel", category: "Очищение", price: 890),
        DemoProduct(id: 2, brand: "DemiLab", name: "Barrier Repair Cream", category: "Увлажнение", price: 1450),
        DemoProduct(id: 3, brand: "SkinTheory", name: "Niacinamide Serum 10%", category: "Сыворотки", price: 1190),
        DemoProduct(id: 4, brand: "SunCare KG", name: "Daily SPF 50", category: "SPF", price: 1590),
    ]
}

private struct GlassCompatContainer<Content: View>: View {
    @ViewBuilder let content: Content

    var body: some View {
        if #available(iOS 26.0, *) {
            GlassEffectContainer {
                content
            }
        } else {
            content
        }
    }
}

private extension View {
    @ViewBuilder
    func nativeGlass(cornerRadius: CGFloat) -> some View {
        if #available(iOS 26.0, *) {
            self.glassEffect(.regular.interactive(), in: .rect(cornerRadius: cornerRadius))
        } else {
            self
                .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: cornerRadius, style: .continuous))
                .overlay(
                    RoundedRectangle(cornerRadius: cornerRadius, style: .continuous)
                        .stroke(.white.opacity(0.62), lineWidth: 1)
                )
        }
    }

    @ViewBuilder
    func nativeGlassIfAvailable(cornerRadius: CGFloat) -> some View {
        if #available(iOS 26.0, *) {
            self.glassEffect(.regular.interactive(), in: .rect(cornerRadius: cornerRadius))
        } else {
            self
        }
    }
}

private extension ShapeStyle where Self == Color {
    static var demiNavy: Color { Color(red: 0.031, green: 0.082, blue: 0.149) }
    static var demiMid: Color { Color(red: 0.141, green: 0.271, blue: 0.435) }
    static var demiAccent: Color { Color(red: 0.749, green: 0.847, blue: 0.984) }
    static var demiSoft: Color { Color(red: 0.902, green: 0.941, blue: 0.984) }
    static var demiMuted: Color { Color(red: 0.573, green: 0.608, blue: 0.678) }
}
