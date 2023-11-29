from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, SelectField, DateField, TimeField, SearchField, TelField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, EqualTo
from app.models import Client

# авторизация
class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    role = BooleanField('Я администратор')
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Вход')

# регистрация клиента
class RegistrationForm(FlaskForm):
    #имя
    lastname = StringField('Фамилия', validators=[DataRequired()])
    firstname = StringField('Имя', validators=[DataRequired()])
    patronymic = StringField('Отчество', validators=[DataRequired()])
    #возраст
    age = IntegerField('Возраст')
    #паспорт
    passport1 = StringField('Серия паспорта', validators=[DataRequired()])
    passport2 = StringField('Номер паспорта', validators=[DataRequired()])
    #логин
    username = StringField('Логин', validators=[DataRequired()])
    #пароль
    password1 = PasswordField('Задайте пароль', validators=[DataRequired()])
    password2 = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password1')])
    #город
    city = SelectField('Можно изменить позже', validators=[DataRequired()])
    #добавить клиенту связь с городом
    submit = SubmitField('Зарегистрироваться')

    def validate_username(self, username):
        user = Client.get_by_username(self.username.data)
        if user is not None:
            raise ValidationError('Клиент с таким логином уже существет!')
        return

    def validate_age(self, age):
        if age.data < 20:
            raise ValidationError('Допускаются водители не моложе 20 лет!')
        return

#добавление автомобиля в заказ2
class CarAddForm1(FlaskForm):
    submit = SubmitField('Забронировать')

#смена города пребывания
class ChangeCityForm(FlaskForm):
    city = SelectField('Выберите новый город', validators=[DataRequired()])
    submit = SubmitField('Сменить')

#добавление автомобиля в заказ2
class CarAddForm2(FlaskForm):
    submit = SubmitField('Забронировать')
    count = IntegerField('Сколько')
    dayhour = SelectField('Дней/Часов', choices=[(1,'Дни'), (2,'Часы')])
    day = DateField('День начала аренды', format = '%Y-%m-%d')
    time = TimeField('Время начала аренды')

    def validate_count(self, count):
        if self.count.data < 1:
            raise ValidationError('Введите количество >= 1!')
        return

# форма добавления отзыва на сайт
class AddFeedback(FlaskForm):
    stars = SelectField('Оценка автомобиля', choices=[(1,1), (2,2), (3,3), (4,4), (5,5)])
    comment = TextAreaField('Оставьте комментарий об автомобиле')
    dealer_stars = SelectField('Оценка оказанного сервиса', choices=[(1,1), (2,2), (3,3), (4,4), (5,5)])
    dealer_comment = TextAreaField('Оставьте комментарий об оказанном Вам сервисе')
    submit = SubmitField('Оставить отзыв')

#форма для оплаты
class PayForm(FlaskForm):
    submit = SubmitField('Оплатить')

#форма отмены аренды
class CancelRentForm(FlaskForm):
    submit = SubmitField('Отменить')

#форма завершения аренды админом
class EndOfferForm(FlaskForm):
    paying_for_fine = BooleanField('Штраф')
    submit = SubmitField('Подтвердить завершение')

#список автомобилей
class AboutCarForm(FlaskForm):
    lower_bound = SearchField('Цена за сутки от')
    upper_bound = SearchField('Цена за сутки до')
    search = SearchField('Поиск по названию')
    submit = SubmitField('Найти')

#форма пополнения баланса
class PaymentSystem(FlaskForm):
    rubles = StringField('Количество рублей', validators=[DataRequired()])
    number = StringField('Номер карты', validators=[DataRequired()])
    year = StringField('Срок действия', validators=[DataRequired()])
    cvc = StringField('CVC код', validators=[DataRequired()])
    submit = SubmitField('Пополнить')

#форма добавления нового автомобиля пользователем
class NewCarForm(FlaskForm):
    brand = StringField('Бренд', validators=[DataRequired()])
    model = StringField('Модель', validators=[DataRequired()])
    year = IntegerField('Год выпуска', validators=[DataRequired()])
    types = SelectField('Тип автомобиля', choices=[(1, 'Бюджетный'), (2, 'Внедорожник'), (3, 'Кабриолет'), (4, 'Премиум'), (5, 'Спорткар')])
    costday = IntegerField('Стоимость за сутки', validators=[DataRequired()])
    costhour = IntegerField('Стоимость за час', validators=[DataRequired()])
    deposit = IntegerField('Депозит', validators=[DataRequired()])
    transmission = SelectField('Трансмиссия', choices=[(1, 'Автомат'), (2, 'Механика'), (3, 'Робот')])
    engine = StringField('Объем двигателя', validators=[DataRequired()])
    seats = IntegerField('Количество мест', validators=[DataRequired()])
    force = IntegerField('Количество сил', validators=[DataRequired()])
    oil = IntegerField('Расход на 100км' , validators=[DataRequired()])
    drive = SelectField('Привод', choices=[(1,'Передний'), (2,'Полный'), (3,'Задний')])
    link = StringField('Ссылка на фото', validators=[DataRequired()])
    info = TextAreaField('Информация об автомобиле', validators=[DataRequired()])
    dealer = SelectField('Адрес автосалона')
    submit = SubmitField('Добавить')

#форма смены пароля
class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Старый пароль', validators=[DataRequired()])
    new_password = PasswordField('Новый пароль пароль', validators=[DataRequired()])
    new_password2 = PasswordField('Повторите новый пароль', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Обновить пароль')

#форма оформления аренды
class AddOfferForm(FlaskForm):
    user = SelectField('Пользователь')
    car = SelectField('Автомобиль')
    submit = SubmitField('Оформить')
    count = IntegerField('Сколько')
    dayhour = SelectField('Дней/Часов', choices=[(1,'Дни'), (2,'Часы')])
    day = DateField('День начала аренды', format = '%Y-%m-%d')
    time = TimeField('Время начала аренды')

    def validate_count(self, count):
        if self.count.data < 1:
            raise ValidationError('Введите количество >= 1!')
        return

