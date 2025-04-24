# store/admin.py
from django.contrib import admin
# Биз models.py файлында түзгөн класстарды импорт кылабыз:
from .models import Category, Product, Order, OrderItem, Review
from django.utils.translation import gettext_lazy as _ # Кыргызча котормо үчүн

# 1. Категория моделин админге каттайбыз
@admin.register(Category) # Бул декоратор CategoryAdmin классын Category модели менен байланыштырат
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'id') # Админ панелде категория тизмесинде кайсы талаалар көрүнөт
    search_fields = ('name',) # Аты боюнча издөө тилкесин кошот

# 2. Азык моделин админге каттайбыз
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Тизмеде көрүнө турган талаалар:
    list_display = (
        'name',
        'category',
        'price',
        'weight_unit', # Өлчөм бирдигин да көрсөтөбүз
        'discount_percent',
        'is_popular',
        'stock',
        'created_at' # Кошулган убактысын да көрсөтсөк болот
    )
    # Тизмеден түз эле өзгөртүүгө мүмкүн болгон талаалар:
    list_editable = ('price', 'discount_percent', 'is_popular', 'stock')
    # Оң жакта пайда боло турган чыпкалар (фильтрлер):
    list_filter = ('category', 'is_popular', 'created_at')
    # Издөө тилкеси кайсы талаалар боюнча иштешин көрсөтөбүз:
    search_fields = ('name', 'description', 'category__name') # Категориянын аты боюнча да издесе болот
    # Слаг талаасын автоматтык түрдө толтуруу (эгер slug талаасы моделде кошсок):
    # prepopulated_fields = {'slug': ('name',)}
    # Даталар боюнча навигация (милдеттүү эмес):
    # date_hierarchy = 'created_at'

# 3. Заказдын курамын (OrderItem) Заказдын ичинде көрсөтүү үчүн класс
class OrderItemInline(admin.TabularInline): # Же admin.StackedInline деп койсо да болот, көрүнүшү башкачараак
    model = OrderItem # Кайсы моделди көрсөтөбүз
    # Админ панелде азыкты ID менен тандоо (миңдеген азык болсо, тизмеден издеген ыңгайсыз):
    raw_id_fields = ('product',)
    # Заказдын ичиндеги азыктын баасын өзгөртпөш керек (тарых үчүн):
    readonly_fields = ('price_at_order', 'get_total_item_price') # get_total_item_price функциясынын жыйынтыгын да көрсөтөбүз
    # Канча бош кошумча сап көрсөтүү керек (0 = кереги жок):
    extra = 0

    # Inline ичинде көрсөтүлө турган талаалар:
    fields = ('product', 'quantity', 'price_at_order', 'get_total_item_price')

    # get_total_item_price функциясынын жыйынтыгын көрсөтүү үчүн кошумча метод:
    def get_total_item_price(self, obj):
        # obj бул жерде OrderItem инстанциясы
        if obj.pk: # Эгер объект сакталган болсо (жаңы кошулуп жатпаса)
            return obj.get_total_item_price()
        return 0 # Же бош калтыруу: "-"
    get_total_item_price.short_description = _('Саптын суммасы') # Баш атын кыргызчалоо


# 4. Заказ (Буйрутма) моделин админге каттайбыз
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
   
    # Тизмеде көрсөтүлө турган талаалар:
    list_display = (
        'id',
        'get_customer_info', # Кардардын аты-жөнү же телефону
        'status',          # Статусу
        'created_at',      # Түзүлгөн датасы
        'total_amount',    # Жалпы суммасы
        'is_paid_display', # Төлөндүбү? (Азырынча муну албай туралы)
        'shipping_address_short', # Даректин башы
    )
    # Оң жакта пайда боло турган чыпкалар (фильтрлер):
    list_filter = (
        'status',          # Статусу боюнча чыпкалоо
        'created_at',      # Датасы боюнча чыпкалоо
        # 'user',          # Катталган колдонуучу боюнча чыпкалоо (эгер керек болсо)
    )
    # Тизмеден түз эле өзгөртүүгө мүмкүн болгон талаалар:
    list_editable = ('status',) # Статусун тизмеден өзгөртө алабыз

    # Издөө тилкеси кайсы талаалар боюнча иштеши керек:
    search_fields = (
        'id',                  # Номери боюнча
        'first_name',          # Аты боюнча
        'last_name',           # Фамилиясы боюнча
        'guest_phone',         # Телефону боюнча
        'shipping_address',    # Дареги боюнча
        'user__username',      # Катталган колдонуучунун аты боюнча (эгер user талаасы бар болсо)
    )
    # Заказдын ичин (OrderItem) дароо көрсөтүү үчүн:
    inlines = [OrderItemInline]

    # Заказды түзөтүүдө өзгөртүүгө болбой турган талаалар:
    readonly_fields = ('created_at', 'updated_at', 'total_amount', 'user', 'get_items_detail') # user'ди да коштук

    # Заказды түзөтүү барагында талааларды иреттөө жана топтоо:
    fieldsets = (
        (_('Буйрутма маалыматы'), {
            'fields': ('id', 'status', 'created_at', 'updated_at')
        }),
        (_('Кардар маалыматы'), {
            'fields': ('user', 'first_name', 'last_name', 'guest_phone') # 'guest_email'ди алып салдык
        }),
        (_('Жеткирүү жана Сумма'), {
            'fields': ('shipping_address', 'total_amount')
        }),
        (_('Товарлар (автоматтык)'), {
            'fields': ('get_items_detail',), # Inline'дан тышкары көрсөтүү үчүн
            'classes': ('collapse',), # Башында жабык турат
        }),
    )

    # list_display'да колдонуу үчүн кошумча методдор:
    def get_customer_info(self, obj):
        """Кардардын аты-жөнүн же телефонун кайтарат"""
        name = f"{obj.first_name} {obj.last_name}".strip()
        if name:
            return name
        elif obj.user:
            return obj.user.username
        elif obj.guest_phone:
            return obj.guest_phone
        return _("Белгисиз")
    get_customer_info.short_description = _('Кардар')

    def shipping_address_short(self, obj):
        """Даректин башын кыскартып көрсөтөт"""
        if obj.shipping_address:
            return obj.shipping_address[:50] + '...' if len(obj.shipping_address) > 50 else obj.shipping_address
        return '-'
    shipping_address_short.short_description = _('Жеткирүү дареги (башы)')

    # Заказды түзөтүү барагында товарларды көрсөтүү үчүн метод (readonly_fields үчүн)
    def get_items_detail(self, obj):
        from django.utils.html import format_html
        html = "<ul>"
        for item in obj.items.all():
            html += f"<li>{item.quantity} x {item.product.name} ({item.price_at_order} сом) = {item.get_total_item_price()} сом</li>"
        html += "</ul>"
        return format_html(html)
    get_items_detail.short_description = _("Заказдын курамы")
    list_filter = ('status', 'created_at', 'user') # Статус, дата жана колдонуучу боюнча чыпкалоо
    search_fields = ('id', 'user__username', 'guest_email', 'guest_phone', 'shipping_address') # Көп талаа боюнча издөө
    # Заказдын ичин (OrderItem) дароо көрсөтүү үчүн жогоруда түзгөн классты колдонобуз:
    inlines = [OrderItemInline]
    # Заказды түзөтүүдө кээ бир талааларды өзгөртүүгө болбосун десек:
    readonly_fields = ('created_at', 'updated_at', 'total_amount') # Мисалы, сумманы кол менен өзгөртпөш керек
    # Тизмеде көрүнө турган get_user_info жана is_paid_display үчүн функциялар:
    def get_user_info(self, obj):
        if obj.user:
            return obj.user.username
        elif obj.guest_email:
            return obj.guest_email
        elif obj.guest_phone:
            return obj.guest_phone
        else:
            return _("Конок")
    get_user_info.short_description = _('Кардар') # Баш аты

    def is_paid_display(self, obj):
        # Эгер Order моделинде is_paid деген BooleanField болсо, бул иштейт
        # Азыр бизде андай талаа жок, кийин кошсок болот.
        # return "✅" if obj.is_paid else "❌"
        return "-" # Азырынча сызыкча
    # is_paid_display.short_description = _('Төлөндүбү?')
    # is_paid_display.boolean = True # Ооба/Жок белгиси катары көрсөтөт (эгер True/False кайтарса)

# 5. Сын-пикир моделин админге каттайбыз
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'created_at', 'comment_short') # Пикирдин башын көрсөтүү
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'product__name', 'comment')
    readonly_fields = ('user', 'product', 'created_at') # Ким, кайсы товарга, качан жазганын өзгөртпөш керек

    # Пикирдин башын кыскартып көрсөтүү үчүн функция
    def comment_short(self, obj):
        if len(obj.comment) > 50:
            return obj.comment[:50] + "..."
        return obj.comment
    comment_short.short_description = _('Пикир (башы)')

# Эскертүү: OrderItem моделин өзүнчө каттаган жокпуз, анткени ал Order ичинде
# inline катары көрсөтүлүп жатат. Эгер өзүнчө да башкаргыңыз келсе,
# @admin.register(OrderItem) деп өзүнчө класс түзсөңүз болот.
# admin.site.register(OrderItem) # Жөнөкөй каттоо