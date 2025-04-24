# store/cart.py
from decimal import Decimal
from django.conf import settings
from .models import Product # Product моделин импорт кылуу

class Cart:
    def __init__(self, request):
        """
        Себетти инициализациялоо.
        Себетти сессиядан жүктөйт же жаңысын түзөт.
        """
        self.session = request.session
        # Сессиядан 'cart' ачкычы менен себетти алууга аракет кылабыз
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # Эгер сессияда себет жок болсо, жаңы бош себет түзөбүз
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, update_quantity=False):
        """
        Товарды себетке кошуу же санын жаңыртуу.
        """
        # Продукттун ID'син сапка айландырабыз, анткени сессия JSON колдонот
        product_id = str(product.id)

        # Эгер продукт себетте жок болсо
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0,
                                       'price': str(product.get_discounted_price())} # Бааны сап катары сактайбыз

        # Эгер санды жаңыртуу керек болсо (update=True келсе)
        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        # Эгер жөн эле кошуу керек болсо
        else:
            self.cart[product_id]['quantity'] += quantity

        # Өзгөрүүнү сессияга сактайбыз
        self.save()

    def save(self):
        """
        Сессиядагы өзгөрүүлөрдү сактоо.
        Сессияны "өзгөрдү" деп белгилейбиз.
        """
        self.session.modified = True

    def remove(self, product):
        """
        Товарды себеттен алып салуу.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """
        Себеттеги товарларды цикл менен айланууга мүмкүндүк берет.
        Базадан продукт объектилерин алып, себетке кошот.
        """
        product_ids = self.cart.keys()
        # Себеттеги ID'лерге туура келген продукттарды базадан алабыз
        products = Product.objects.filter(id__in=product_ids)

        cart = self.cart.copy() # Убактылуу көчүрмө менен иштейбиз
        for product in products:
            cart[str(product.id)]['product'] = product # Продукт объектисин кошобуз

        for item in cart.values():
            # Бааны кайра Decimal'га айландырабыз
            item['price'] = Decimal(item['price'])
            # Ар бир товардын жалпы баасын эсептейбиз
            item['total_price'] = item['price'] * item['quantity']
            yield item # Итератор катары кайтарабыз

    def __len__(self):
        """
        Себеттеги товарлардын жалпы санын кайтарат.
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """
        Себеттеги бардык товарлардын жалпы суммасын эсептейт.
        """
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        """
        Себетти сессиядан тазалоо.
        """
        del self.session[settings.CART_SESSION_ID]
        self.save()