from data.bookings import Booking
from data.owners import Owner
from data.cages import Cage
from data.snakes import Snake
import datetime


def create_account(name,email):
    o = Owner()
    o.name = name
    o.email = email

    o.save()

    return o

def check_email_exist(email):
    o = Owner.objects().filter(email=email).first()
    return o

def create_cage(active_account,name,price,sq_mts,carpet,toys,dang_snakes):
    c = Cage()
    c.name = name
    c.price = price
    c.square_meters = sq_mts
    c.allow_dangerous_snakes = dang_snakes
    c.is_carpeted = carpet
    c.has_toys = toys

    c.save()

    account = check_email_exist(active_account.email)
    account.cage_ids.append(c.id)
    account.save()

    return c

def get_list_cages(account):

    cages = list(Cage.objects(id__in=account.cage_ids))
    return cages


def create_snake(active_account,name,species,length,is_venom):
    s = Snake()
    s.name = name
    s.species = species
    s.length = length
    s.is_venomous = is_venom
    s.save()

    account = check_email_exist(active_account.email)
    account.snake_ids.append(s.id)
    account.save()

    return s


def get_snake_list(account):

    snakes = list(Snake.objects(id__in=account.snake_ids))
    return snakes 


def add_available_date(cage,start_date,days):
    b = Booking()
    b.check_in_date=start_date
    b.check_out_date=start_date+datetime.timedelta(days=days)

    c = Cage.objects(id=cage.id).first()
    c.bookings.append(b) 
    c.save()                #save is done for the parent document

    return c

def get_available_cages(snake,checkin,checkout):
    min_size = snake.length/4
    query = Cage.objects() \
        .filter(square_meters__gte=min_size) \
        .filter(bookings__check_in_date__lte=checkin) \
        .filter(bookings__check_out_date__gte=checkout)

    cages = query.order_by('price', '-square_meters')

    

    """ 
    The condition below is checked because the above query will return true if two differnt 
    booking instances for same cage satisfies the conditions separately. It is requred that 
    one booking instance only covers the entire time from checkin to checkout.
    Alternately check how to filter element-wise for embedded list
    """
    final_cages = []
    for c in cages:
        for b in c.bookings:
            if b.check_in_date <= checkin and b.check_out_date >= checkout and b.guest_snake_id is None:
                final_cages.append(c)

    return final_cages

    

def book_cage_for_snake(account,snake,cage,checkin,checkout):

    booking = None

    for b in cage.bookings:
        if b.check_in_date <= checkin and b.check_out_date >= checkout and b.guest_snake_id is None:
            booking = b
            break

    booking.guest_owner_id = account.id
    booking.guest_snake_id = snake.id
    booking.check_in_date = checkin
    booking.check_out_date = checkout
    booking.booked_date = datetime.datetime.now()


    cage.save() #save is done for the parent document



def get_bookings(snakes):
    booked_cages = []
    for s in snakes:
        booked_cages.append((s,Cage.objects().filter(bookings__guest_snake_id=s.id)))
    
    return booked_cages

    