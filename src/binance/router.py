from binance import AsyncClient, BinanceSocketManager
from fastapi import APIRouter

from src.config import BINANCE_API, BINANCE_SECRET_KEY

router = APIRouter(
    tags=['Chart']
)

@router.get('/socket_binance')
async def socket_binance(currency: str, stop: bool = False):
    '''
    Сокет соединение с бинансом. Длится 60 секунд, но походу бесконечно.
    - currency: принимает валюту по которой запрашиваются данные в формате тикера - BTCUSDT, ETHUSDT
    - stop: true - закрыть соединение, false - открыть. Можно реализовать логику, если клиент покидает этот uri то закрывать соединение.

    Возвращает данные в формате:
    {

      "e": "trade", - тип события, который указывает на тип транзакции.

      "E": 1685352493842, -  время события в миллисекундах.

      "s": "BTCUSDT", - символ пары торгов

      "t": 3128786077, - ID сделки.

      "p": "27892.87000000", - цена по которой произошла сделка.

      "q": "0.00181000", - количество базовой валюты, которое было продано или куплено.

      "b": 21277176651, - ID покупателя.

      "a": 21277175869, - ID продавца.

      "T": 1685352493842, - время выполнения операции в миллисекундах.

      "m": false, - флаг режима: true - если сделка происходит за пределами стакана (вне очереди), и false - если сделка происходит внутри стакана.

      "M": true - флаг maker: true - если покупатель является создателем спроса (maker), и false - если покупатель является исполнителем заявки (taker).

    }
    '''

    binance_client = await AsyncClient.create(api_key=BINANCE_API, api_secret=BINANCE_SECRET_KEY)
    binance_manager = BinanceSocketManager(binance_client, user_timeout=60)

    ts = binance_manager.trade_socket(symbol=currency)
    if not stop:
        async with ts as tscm:
            while True:
                res = await tscm.recv()
                return res
    else:
        await binance_client.close_connection()
        return 200
