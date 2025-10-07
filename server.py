import grpc
from concurrent import futures
import time
from datetime import datetime
import uuid
from collections import OrderedDict
import orderManager_pb2
import orderManager_pb2_grpc

class OrderStorage:
    def __init__(self):
        self.orders = OrderedDict()
        self._add_sample_orders()  
    
    def _add_sample_orders(self):

        sample_orders = [
            {
                'product_name': 'iPhone 15 Pro',
                'quantity': 1,
                'price': 99990.0,
                'customer_name': 'Иван Петров',
                'status': 'Ожидает сортировки'
            },
            {
                'product_name': 'Ноутбук ASUS ROG',
                'quantity': 1,
                'price': 124990.0,
                'customer_name': 'Мария Сидорова',
                'status': 'Отсортирован'
            },
            {
                'product_name': 'Наушники Sony WH-1000XM5',
                'quantity': 2,
                'price': 29990.0,
                'customer_name': 'Алексей Козлов',
                'status': 'awaiting_delivery'
            },
            {
                'product_name': 'Мышь Logitech MX Master 3',
                'quantity': 3,
                'price': 8990.0,
                'customer_name': 'Ольга Новикова',
                'status': 'delivering'
            },
            {
                'product_name': 'Монитор Samsung Odyssey',
                'quantity': 1,
                'price': 45990.0,
                'customer_name': 'Дмитрий Волков',
                'status': 'delivered'
            }
        ]
        
        for order_data in sample_orders:
            order_id = str(uuid.uuid4())[:8]
            total_amount = order_data['quantity'] * order_data['price']
            
            order = {
                'order_id': order_id,
                'product_name': order_data['product_name'],
                'quantity': order_data['quantity'],
                'price': order_data['price'],
                'customer_name': order_data['customer_name'],
                'status': order_data['status'],
                'created_at': datetime.now().strftime("%d %m-%Y %H:%M:%S"),
                'total_amount': total_amount
            }
            self.orders[order_id] = order
        
    def add_order(self, product_name, quantity, price, customer_name):
        order_id = str(uuid.uuid4())[:8]
        total_amount = quantity * price
        order = {
            'order_id': order_id,
            'product_name': product_name,
            'quantity': quantity,
            'price': price,
            'customer_name': customer_name,
            'status': 'CREATED',
            'created_at': datetime.now().strftime("%d %m-%Y %H:%M:%S"),
            'total_amount': total_amount
        }
        self.orders[order_id] = order
        return order
    
    def get_order(self, order_id):
        return self.orders.get(order_id)
    
    def get_all_orders(self):
        return list(self.orders.values())

class OrderService(orderManager_pb2_grpc.OrderServiceServicer):
    def __init__(self):
        self.storage = OrderStorage()
    
    def GetOrder(self, request, context):
        order_id = request.order_id
        order = self.storage.get_order(order_id)
        
        if order:
            return orderManager_pb2.OrderResponse(
                order_id=order['order_id'],
                product_name=order['product_name'],
                quantity=order['quantity'],
                price=order['price'],
                customer_name=order['customer_name'],
                status=order['status'],
                created_at=order['created_at'],
                total_amount=order['total_amount']
            )
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Заказ {order_id} не найден или не существует")
            return orderManager_pb2.OrderResponse()
    
    def CreateOrder(self, request, context):
        try:
            order = self.storage.add_order(
                product_name=request.product_name,
                quantity=request.quantity,
                price=request.price,
                customer_name=request.customer_name
            )
            
            return orderManager_pb2.OrderResponse(
                order_id=order['order_id'],
                product_name=order['product_name'],
                quantity=order['quantity'],
                price=order['price'],
                customer_name=order['customer_name'],
                status=order['status'],
                created_at=order['created_at'],
                total_amount=order['total_amount']
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Ошибка создания заказа: {str(e)}")
            return orderManager_pb2.OrderResponse()
    
    def GetAllOrders(self, request, context):
        orders = self.storage.get_all_orders()
        for order in orders:
            yield orderManager_pb2.OrderResponse(
                order_id=order['order_id'],
                product_name=order['product_name'],
                quantity=order['quantity'],
                price=order['price'],
                customer_name=order['customer_name'],
                status=order['status'],
                created_at=order['created_at'],
                total_amount=order['total_amount']
            )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    orderManager_pb2_grpc.add_OrderServiceServicer_to_server(OrderService(), server)
    server.add_insecure_port('[::]:50051')
    print("Сервер запущен на порте 50051...")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()