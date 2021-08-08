from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from models import Base, Order
engine = create_engine('sqlite:///orders.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

def create_child_order(parent_order, buy_amount):

    partial_order = {'buy_currency': parent_order.buy_currency,
    'sell_currency': parent_order.sell_currency, 
    'buy_amount': buy_amount,
    'sell_amount': (buy_amount * parent_order.sell_amount / parent_order.buy_amount)*2,
    'sender_pk': parent_order.sender_pk,
    'receiver_pk': parent_order.receiver_pk,
    'creator_id': parent_order.id}
    assert partial_order['buy_amount']/parent_order.buy_amount <= partial_order['sell_amount']/parent_order.sell_amount
    #session.add(Order(**partial_order))
    process_order(partial_order)

def process_order(order):

    new_order = Order(**order)

    c1 = Order.filled == None
    c2 = Order.buy_currency == new_order.sell_currency
    c3 = Order.sell_currency == new_order.buy_currency
    c4 = Order.sell_amount / Order.buy_amount >= new_order.buy_amount/new_order.sell_amount

    counterparty_order = session.query(Order).filter(c1).filter(c2).filter(c3).filter(c4).first()
    session.add(new_order)    
    session.commit()

    if counterparty_order is not None:
        now = datetime.now()
        counterparty_order.filled = now
        new_order.filled = now
        new_order.counterparty_id = counterparty_order.id
        counterparty_order.counterparty_id = new_order.id
        if (new_order.buy_amount > counterparty_order.sell_amount):
            create_child_order(new_order, new_order.buy_amount - counterparty_order.sell_amount)
        if (counterparty_order.buy_amount > new_order.sell_amount):
            create_child_order(counterparty_order, counterparty_order.buy_amount - new_order.sell_amount)
       
    session.commit()


def print_orders():

    print("dB:")
    orders = session.execute('SELECT * FROM orders')

    for order in orders:
        print (order.id, order.counterparty_id,order.creator_id,order.buy_currency, order.buy_amount,order.sell_currency,order.sell_amount,order.filled)