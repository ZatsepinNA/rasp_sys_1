import grpc
import orderManager_pb2
import orderManager_pb2_grpc

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = orderManager_pb2_grpc.OrderServiceStub(channel)
        
        while True:
            print("\nСистема управления заказами 'Order manager'")
            print("1. Создать новый заказ")
            print("2. Получить информацию о заказе и его статус по номеру")
            print("3. Получить все заказы")
            print("4. Выход")
            
            choice = input("Выберите опцию: ")
            
            if choice == "1":
                product = input("Название товара: ")
                quantity = int(input("Количество: "))
                price = float(input("Цена за единицу: "))
                customer = input("Имя клиента: ")
                
                response = stub.CreateOrder(orderManager_pb2.CreateOrderRequest(
                    product_name=product,
                    quantity=quantity,
                    price=price,
                    customer_name=customer
                ))
                
                print(f"\nЗаказ успешно создан!")
                print(f"ID заказа: {response.order_id}")
                print(f"Общая сумма: {response.total_amount:.2f} руб.")
                print(f"Статус: {response.status}")
            
            elif choice == "2":
                order_id = input("Введите ID заказа: ")
                response = stub.GetOrder(orderManager_pb2.OrderRequest(order_id=order_id))
                
                if response.order_id:
                    print(f"\n Детали заказа:")
                    print(f"ID: {response.order_id}")
                    print(f"Товар: {response.product_name}")
                    print(f"Количество: {response.quantity}")
                    print(f"Цена: {response.price:.2f} руб.")
                    print(f"Общая сумма: {response.total_amount:.2f} руб.")
                    print(f"Клиент: {response.customer_name}")
                    print(f"Статус: {response.status}")
                    print(f"Создан: {response.created_at}")
                else:
                    print("Заказ не найден! или не существует")
            
            elif choice == "3":
                # Все заказы
                print("\nВсе заказы:")
                for i, order in enumerate(stub.GetAllOrders(orderManager_pb2.Empty())):
                    print(f"{i+1}. {order.order_id}: {order.product_name} - {order.total_amount:.2f} руб.")
            
            elif choice == "4":
                break
            
            else:
                print("Некорркетный выбор")

if __name__ == '__main__':
    run()