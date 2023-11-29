from app import app
from flask import render_template, flash, redirect, url_for, session
from flask import request
from werkzeug.urls import url_parse
from flask_login import current_user, login_user, logout_user, login_required
from datetime import datetime

from app.forms import RegistrationForm, LoginForm, CarAddForm1, CarAddForm2, PayForm, PaymentSystem, ChangeCityForm, AddFeedback, CancelRentForm, AboutCarForm
from app.forms import EndOfferForm, NewCarForm, ChangePasswordForm, AddOfferForm
from app.models import Client, City, Administrator, Car, Offer, Dealer

# главная страница
@app.route("/")
@app.route("/index")
def index():
    if current_user.is_anonymous:
        return render_template('index2.html', title = 'Главная страница')
    else:
        if current_user.role == 'client':
            types = Car.get_all_types(current_user.id)
        else:
            types = Car.get_all_types_by_admin_id(current_user.id)
        return render_template('index.html', title = 'Главная страница', types = types)

@login_required
@app.route("/registration", methods = ['GET', 'POST'])
def registration():
    form = RegistrationForm()
    cities = City.get_list()
    if cities is None:
        cities = []
    form.city.choices = cities
    if form.validate_on_submit():
        user = Client(
                username = form.username.data,
                name = f'{form.lastname.data} {form.firstname.data} {form.patronymic.data}',
                passport = f'{form.passport1.data} {form.passport2.data}',
                city_id = form.city.data, 
                age = form.age.data)
        user.set_password(form.password1.data)
        user.adduser()
        flash('Вы создали нового пользователя')
        return redirect(url_for('login'))
    return render_template('registration.html', title = 'Регистрация аккаунта', form = form)


# вход пользователя
@app.route("/login", methods = ['GET', 'POST'])
def login():
    # если пользователь аутентифицирован
    if current_user.is_authenticated:
        return redirect("/index")
    # определяем необходимую форму из файла forms
    form = LoginForm()
    # если не возникло проблем с валидаторами, определенными в файле forms
    if form.validate_on_submit():
        # если поставлена галочка админ
        if form.role.data == True:
            # задаем переменной роль в сессии значение админ
            # это нужно для определения, из какой таблицы получать пользователя в методе loas user
            session['role'] = 'admin'
            user = Administrator.get_by_username(form.username.data)
        else:
            # если не поставлена галочка, значит роль пользователя - клиент
            session['role'] = 'client'
            user = Client.get_by_username(form.username.data)

        # если не нашелся пользователь с таким логином или пароль пользователя неверный
        if user is None or not user.check_password(form.password.data):
            # выдать ошибку на экран
            flash('Введен неправильный логин или пароль')
            return redirect("/login")
        print("имя найденного пользователя")
        print(user.name)
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            if session['role'] == 'client':
                next_page = "/index"
            elif session['role'] == 'admin':
                next_page = f'/admin/{user.username}'
        return redirect(next_page)
    return render_template('login.html', title = 'Вход в систему', form=form)

# мой профиль пациента
@app.route("/client/<username>", methods = ['GET'])
@login_required
def client(username):
    user = Client.get_by_username(username)
    city = City.get_by_username(username)
    my_rent = Offer.get_unfinished_list_by_username(username)
    print('0000000000000000000000000000000000000000000000')
    print(my_rent)
    print('0000000000000000000000000000000000000000000000')
    return render_template('client.html', title = 'Личный кабинет', user=user, city=city, my_rent=my_rent)

#смена пароля пользователя
@app.route('/change_password/<username>', methods = ['GET', 'POST'])
@login_required
def change_password(username):
    user = current_user
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user.set_password(form.new_password.data)
        user.update_password()
        if session['role'] == 'client':
            return redirect(url_for('client', username = username))
        else:
            return redirect(url_for('admin', username = username))
    return render_template('change_password.html', title='Смена пароля', form=form)

# отмена аренды
@app.route("/cancel_rent/<username>/<offer_id>/<car_id>/<rubles>", methods = ['GET', 'POST'])
@login_required
def cancel_rent(username, offer_id, car_id, rubles):
    deposit = Car.get_deposit_by_id(car_id)
    rubles = int(rubles) - int(deposit)
    info = Car.get_name_by_id(car_id)
    user = current_user
    form = CancelRentForm()
    if form.validate_on_submit():
        user.add_balance(rubles)
        Offer.set_is_complited(offer_id)
        return redirect(url_for('client', username=username))
    return render_template('cancel_rent.html', title = 'Отмена аренды', form=form, info=info, rubles=rubles)

# история аренды пользователя
@app.route("/rent_store/<username>", methods = ['GET'])
@login_required
def rent_store(username):
    my_rent_with_feedback = Offer.get_finished_list_by_username_with_feedback(username)
    my_rent_without_feedback = Offer.get_finished_list_by_username_without_feedback(username)
    return render_template('rent_store.html', title = 'История аренды', my_rent_with_feedback=my_rent_with_feedback, my_rent_without_feedback=my_rent_without_feedback)

# добавляем отзыв
@app.route('/add_feedback/<offer_id>', methods = ['GET', 'POST'])
@login_required
def add_feedback(offer_id):
    form = AddFeedback()
    if form.validate_on_submit():
        Offer.add_feedback_by_id(offer_id, form.stars.data, form.comment.data, form.dealer_stars.data, form.dealer_comment.data)
        Offer.change_feedback_status(offer_id)
        return redirect(url_for('rent_store', username = current_user.username))
    return render_template('add_feedback.html', form=form, title = 'Отзыв')

#страница пополнения баланса
@app.route("/add_balance/<username>", methods = ['GET', 'POST'])
@login_required
def add_balance(username):
    form = PaymentSystem()
    if form.validate_on_submit():
        user = current_user
        user.add_balance(form.rubles.data)
        return redirect(url_for('client', username=username))
    return render_template('add_balance.html', title = 'Платежная система', form=form)

#страница смены текущего города
@app.route("/change_city/<username>", methods = ['GET', 'POST'])
@login_required
def change_city(username):
    form = ChangeCityForm()
    cities = City.get_list()
    if cities is None:
        cities = []
    form.city.choices = cities
    if form.validate_on_submit():
        user = current_user
        user.change_city_id(form.city.data)
        return redirect(url_for('client', username=username))
    return render_template('change_city.html', title = 'Смена города', form=form)

# страница администратора
@app.route("/admin/<username>", methods = ['GET', 'POST'])
@login_required
def admin(username):
    user = Administrator.get_by_username(username)
    return render_template('admin.html', title = 'Администрирование', user=user)

# выбор действия перед оформлением заказа для юзера
@app.route('/add_offer_by_admin/<username>', methods = ['GET', 'POST'])
@login_required
def add_offer_by_admin(username):
    return render_template('add_offer_by_admin.html', title = 'Оформление аренды для пользователя')


#Добавление админом нового юзера
@app.route('/add_user/<admin_username>', methods = ['GET', 'POST'])
@login_required
def add_user(admin_username):
    form = RegistrationForm()
    cities = City.get_list_by_admin_username(admin_username)
    if cities is None:
        cities = []
    form.city.choices = cities
    if form.validate_on_submit():
        user = Client(
                username = form.username.data,
                name = f'{form.lastname.data} {form.firstname.data} {form.patronymic.data}',
                passport = f'{form.passport1.data} {form.passport2.data}',
                city_id = form.city.data)
        user.set_password(form.password1.data)
        user.adduser()
        flash('Вы создали нового пользователя')
        return redirect(url_for('add_offer_by_admin', username=admin_username))
    return render_template('registration.html', form=form, title = 'Добавить пользователя')

#добавление нового оффера админом
@app.route('/add_new_offer_by_admin/<admin_username>', methods = ['GET', 'POST'])
@login_required
def add_new_offer_by_admin(admin_username):
    hours_count = 0
    cost = 0
    deposit = 0
    summ = 0
    cars2 = []
    cars1 = Car.get_car_by_admin_username(admin_username)
    for c in cars1:
        cars2.append((c[0], f'{c[1]} {c[2]}({c[3]})'))
        print(cars2)

    form = AddOfferForm()
    if cars2 is None:
        cars2 = []
    form.car.choices = cars2
    users = Client.get_list()
    if users is None:
        users = []
    form.user.choices = users
    if form.validate_on_submit():
        day_cost = Car.get_day_cost_by_id(form.car.data)
        hour_cost = Car.get_hour_cost_by_id(form.car.data)
        if int(form.dayhour.data) == 1:
            hours_count = int(form.count.data) * 24
            cost = int(form.count.data) * day_cost
        else:
            hours_count = int(form.count.data)
            cost = int(form.count.data) * hour_cost
        deposit = Car.get_deposit_by_id(form.car.data)
        summ = int(cost) + int(deposit)
        dealer_id = Dealer.get_id_by_car_id(form.car.data)
        user = Client.get_by_id(form.user.data)
        Offer.add(form.user.data, user.username, user.passport, dealer_id, form.car.data, hours_count, summ, form.day.data, form.time.data)
        return redirect(url_for('admin', username = admin_username))
    return render_template('add_new_offer_by_admin.html', title = 'Оформить аренду', form=form)

# завершить аренду
@app.route("/end_offer/<admin_username>", methods = ['GET'])
@login_required
def end_offer(admin_username):
    offers_list = Offer.get_by_admin_username(admin_username)
    return render_template('end_offer.html', title='Завершить аренду', offers_list=offers_list)

#добавить новый автомобиль к этому автосалону
@app.route("/add_new_car/<admin_username>", methods = ['GET','POST'])
@login_required
def add_new_car(admin_username):
    types=''
    transmission=''
    drive=''
    dealers = Dealer.get_adres_by_admin_username(admin_username)
    if dealers is None:
        dealers = []
    form = NewCarForm()
    form.dealer.choices = dealers
    if form.validate_on_submit():
        dealer_id = form.dealer.data
        brand = form.brand.data
        model = form.model.data
        year = form.year.data
        for t in form.types.choices:
            if str(t[0])==str(form.types.data):
                types = t[1]
                break
        costday = form.costday.data
        costhour = form.costhour.data
        deposit = form.deposit.data
        for t in form.transmission.choices:
            if str(t[0])==str(form.transmission.data):
                transmission = t[1]
                break
        engine = form.engine.data
        seats = form.seats.data
        force = form.force.data
        oil = form.oil.data
        for d in form.drive.choices:
            if str(d[0])==str(form.drive.data):
                drive = d[1]
                break
        info = form.info.data
        link = form.link.data
        Car.add(dealer_id, brand, model, year, types, costday, costhour, deposit, transmission, engine, seats, force, oil, drive, info, link)
        return redirect(url_for('admin', username = admin_username))
    return render_template('add_new_car.html', form=form, title = 'Добавить автомобиль')

# подтверждение завершения аренды
@app.route("/end_offer/<admin_username>/<offer_id>", methods = ['GET', 'POST'])
@login_required
def end_offer2(admin_username, offer_id):
    information = Offer.get_unfinished_list_by_id(offer_id)
    rubles = Car.get_deposit_by_offer_id(offer_id)

    username = information[0][7]
    form = EndOfferForm()
    if form.validate_on_submit():
        Offer.set_is_complited(offer_id)
        if form.paying_for_fine.data == False:
            Client.add_balance_by_username(username, rubles)
        return redirect(url_for('end_offer', admin_username=admin_username))
    return render_template('accept_offer_end.html', title = 'Подтвердить завершение', information=information, form=form)

#список автомобилей
@app.route("/cars/<type>", methods = ['GET', 'POST'])
@login_required
def cars(type):
    if current_user.role == 'client':
        city_id = Client.get_city_by_username(current_user.username)
    else:
        city_id = Administrator.get_city_by_id(current_user.id)
    print('------------------------------------------------------------')
    print(city_id)
    if type == 'Все автомобили':
        car_list = Car.get_list(city_id)
    else:
        car_list = Car.get_list_by_type(type, city_id)
    form = AboutCarForm()
    
    if form.validate_on_submit():
        name = str(form.search.data).lower()
        if name == '':
            name= 'nothing'
        lower_bound = form.lower_bound.data
        upper_bound = form.upper_bound.data
        if lower_bound=='':
            lower_bound = 0
        if upper_bound == '':
            upper_bound = 1000000
        return redirect(url_for('cars_name', type=type, name = name, lower_bound=lower_bound, upper_bound=upper_bound))
    return render_template('cars.html', title = 'Список автомобилей', car_list = car_list, type=type, form=form)

#список автомобилей по имени
@app.route("/cars/<type>/<name>/<lower_bound>/<upper_bound>", methods = ['GET', 'POST'])
@login_required
def cars_name(type, name, lower_bound, upper_bound):
    id = Client.get_city_by_username(current_user.username)
    if type == 'Все автомобили':
        car_list = Car.get_list_by_name(id, name, lower_bound, upper_bound)
    else:
        car_list = Car.get_list_by_type_name(type, id, name, lower_bound, upper_bound)
    form = AboutCarForm()
    if form.validate_on_submit():
        name = str(form.search.data).lower()
        if name == '':
            name= 'nothing'
        lower_bound = form.lower_bound.data
        upper_bound = form.upper_bound.data
        if lower_bound=='':
            lower_bound = 0
        if upper_bound == '':
            upper_bound = 1000000
        return redirect(url_for('cars_name', type=type, name = name, lower_bound=lower_bound, upper_bound=upper_bound))
    return render_template('cars.html', title = 'Список автомобилей', car_list = car_list, type=type, form=form)


#информация об автомобиле
@app.route('/about_car/<type>/<id>', methods = ['GET', 'POST'])
@login_required
def about_car(type, id):
    info = Car.get_info_by_id(id)
    image = Car.get_link_by_id(id)
    print('12121212121212121212121')
    print(image[0][0])
    car_stars = Car.get_stars_by_id(id)
    feedback = Car.get_feedback_by_id(id)
    if car_stars is None:
        car_stars = 'Еще нет оценок'
    else:
        car_stars = float(Car.get_stars_by_id(id))
    dealer_id = Dealer.get_id_by_car_id(id)
    dealer_stars = Dealer.get_stars_by_id(dealer_id)
    if dealer_stars is None:
        dealer_stars = 'Еще нет оценок'
    else:
        dealer_stars = float(Dealer.get_stars_by_id(dealer_id))
    form = CarAddForm1()
    if form.validate_on_submit():
        return redirect(url_for('add_car', id = id))
    return render_template('about_car.html', title = 'Об автомобиле', image=image[0][0], feedback=feedback, type=type, form=form, info = info, car_stars=car_stars, dealer_stars=dealer_stars, id=id, dealer_id=dealer_id)

#информация об автосалоне
@app.route('/about_dealer/<type>/<id>/<dealer_id>', methods = ['GET'])
@login_required
def about_dealer(type, id, dealer_id):
    feedback = Dealer.get_feedback_by_id(dealer_id)
    return render_template('about_dealer.html', title = 'Об автосалоне', type=type, id=id, feedback=feedback)


@app.route('/add_car/<id>', methods = ['GET','POST'])
@login_required
def add_car(id):
    day_cost = Car.get_day_cost_by_id(id)
    hour_cost = Car.get_hour_cost_by_id(id)
    hours_count = 0
    cost = 0
    form = CarAddForm2()
    if form.validate_on_submit():
        start_day = form.day.data
        start_time = form.time.data
        if int(form.dayhour.data) == 1:
            hours_count = int(form.count.data) * 24
            cost = int(form.count.data) * day_cost
        else:
            hours_count = int(form.count.data)
            cost = int(form.count.data) * hour_cost
        
        return redirect(url_for('pay_for_car', cost = cost, hours_count=hours_count, start_day=start_day, start_time=start_time, car_id=id))
    return render_template('add_car.html', title = 'Забронировать автомобиль', form=form)
#страница оплаты брони
@app.route('/pay_for_car/<car_id>/<start_day>/<start_time>/<hours_count>/<cost>', methods = ['GET', 'POST'])
@login_required
def pay_for_car(car_id, start_day, start_time, hours_count, cost):
    user = current_user
    car = Car.get_name_by_id(car_id)
    deposit = Car.get_deposit_by_id(car_id)
    summ = int(cost) + int(deposit)
    a,b,c = start_day.split('-')
    date = f'{c}-{b}-{a}'
    dealer_id = Dealer.get_id_by_car_id(car_id)
    form = PayForm()
    if form.validate_on_submit():
        print('Валидейт')
        if current_user.balance >= summ:
            print('Денег хватает')
            Offer.add(user.id, user.username, user.passport, dealer_id, car_id, hours_count, summ, start_day, start_time)
            user.write_off_balance(summ)
            return redirect(url_for('index'))
        else:
            print('Денег не хватает')
            return render_template('not_enough_money.html')
    return render_template('pay_for_car.html', form=form, title='Оплата', summ=summ, hours_count=hours_count, date=date, start_time=start_time, car = car)

#страница с условиями аренды
@app.route('/conditions', methods = ['GET'])
def conditions():
    return render_template('conditions.html', title = 'Условия аренды')




# выйти из аккаунта
@app.route("/logout")
@login_required
def logout():
    logout_user()
    session['role'] = None
    return redirect("/index")