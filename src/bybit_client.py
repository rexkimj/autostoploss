"""
Bybit API 클라이언트 설정 및 관련 함수
"""
import ccxt
import os
from dotenv import load_dotenv

load_dotenv()


def create_bybit_client():
    """
    Bybit CCXT 클라이언트 생성
    """
    use_testnet = os.getenv('USE_TESTNET', 'true').lower() == 'true'

    exchange = ccxt.bybit({
        'apiKey': os.getenv('BYBIT_API_KEY'),
        'secret': os.getenv('BYBIT_API_SECRET'),
        'options': {
            'defaultType': 'future',  # 선물 거래
        }
    })

    if use_testnet:
        exchange.set_sandbox_mode(True)
        print("⚠️  테스트넷 모드로 실행 중")
    else:
        print("🔴 실거래 모드로 실행 중")

    return exchange


def get_positions(exchange):
    """
    현재 보유 중인 포지션 조회

    Returns:
        list: 포지션 목록
    """
    try:
        balance = exchange.fetch_balance()
        positions = balance.get('info', {}).get('result', {}).get('list', [])

        # 실제 포지션만 필터링 (size > 0)
        active_positions = []
        for pos in positions:
            size = float(pos.get('size', 0))
            if size > 0:
                active_positions.append({
                    'symbol': pos.get('symbol'),
                    'side': pos.get('side'),  # Buy(롱) 또는 Sell(숏)
                    'size': size,
                    'entryPrice': float(pos.get('avgPrice', 0)),
                    'markPrice': float(pos.get('markPrice', 0)),
                    'unrealizedPnl': float(pos.get('unrealisedPnl', 0)),
                })

        return active_positions
    except Exception as e:
        print(f"❌ 포지션 조회 실패: {e}")
        return []


def set_stop_loss(exchange, symbol, side, stop_price, quantity):
    """
    스탑로스 주문 설정

    Args:
        exchange: CCXT exchange 객체
        symbol: 심볼 (예: 'BTC/USDT:USDT')
        side: 'buy' (숏 청산) 또는 'sell' (롱 청산)
        stop_price: 스탑 가격
        quantity: 수량
    """
    try:
        # 기존 스탑로스 주문 취소
        cancel_existing_stop_orders(exchange, symbol)

        # 새 스탑로스 주문 설정
        params = {
            'stopLoss': {
                'triggerPrice': stop_price,
                'type': 'market',
            }
        }

        order = exchange.create_order(
            symbol=symbol,
            type='market',
            side=side,
            amount=quantity,
            params=params
        )

        print(f"✅ 스탑로스 설정: {symbol} {side.upper()} @ {stop_price:.2f}")
        return order
    except Exception as e:
        print(f"❌ 스탑로스 설정 실패: {e}")
        return None


def cancel_existing_stop_orders(exchange, symbol):
    """
    기존 스탑 주문 취소
    """
    try:
        open_orders = exchange.fetch_open_orders(symbol)
        for order in open_orders:
            if order.get('type') in ['stop', 'stop_market']:
                exchange.cancel_order(order['id'], symbol)
                print(f"🗑️  기존 스탑 주문 취소: {order['id']}")
    except Exception as e:
        print(f"⚠️  기존 스탑 주문 취소 중 오류: {e}")
