"""
Bybit 자동 스탑로스 설정 메인 프로그램

포지션 진입 시 자동으로 스탑로스를 설정합니다:
- 롱 포지션: 최근 4시간 최저점에 스탑로스
- 숏 포지션: 최근 4시간 최고점에 스탑로스
"""
import time
import os
from datetime import datetime
from bybit_client import create_bybit_client, get_positions, set_stop_loss
from data_handler import (
    fetch_4hour_candles,
    get_high_low_from_df,
    display_candle_data,
    analyze_position_risk
)


# 이미 스탑로스가 설정된 포지션 추적
processed_positions = set()


def process_position(exchange, position):
    """
    개별 포지션 처리 및 스탑로스 설정

    Args:
        exchange: CCXT exchange 객체
        position: 포지션 정보 딕셔너리
    """
    symbol = position['symbol']
    side = position['side']  # 'Buy' or 'Sell'
    size = position['size']
    entry_price = position['entryPrice']

    # 포지션 고유 ID (중복 처리 방지)
    position_id = f"{symbol}_{side}_{size}"

    if position_id in processed_positions:
        return  # 이미 처리된 포지션

    print(f"\n🎯 새 포지션 감지: {symbol}")
    print(f"   방향: {'롱(Long)' if side == 'Buy' else '숏(Short)'}")
    print(f"   크기: {size}")
    print(f"   진입가: {entry_price:.2f}")

    # CCXT 형식으로 심볼 변환 (BTCUSDT -> BTC/USDT:USDT)
    if '/' not in symbol:
        # Bybit 심볼 형식 변환
        if symbol.endswith('USDT'):
            base = symbol[:-4]
            ccxt_symbol = f"{base}/USDT:USDT"
        else:
            print(f"⚠️  지원하지 않는 심볼 형식: {symbol}")
            return
    else:
        ccxt_symbol = symbol

    # 최근 4시간 캔들 데이터 가져오기
    df = fetch_4hour_candles(exchange, ccxt_symbol)

    if df.empty:
        print(f"❌ {symbol} 캔들 데이터를 가져올 수 없습니다.")
        return

    # 캔들 데이터 표시
    display_candle_data(df, symbol)

    # 최고가/최저가 추출
    high_price, low_price = get_high_low_from_df(df)

    # 스탑로스 가격 결정
    if side == 'Buy':  # 롱 포지션
        stop_price = low_price
        stop_side = 'sell'  # 롱 청산은 sell
        print(f"\n🔴 롱 포지션 -> 최저점({low_price:.2f})에 스탑로스 설정")
    else:  # 숏 포지션
        stop_price = high_price
        stop_side = 'buy'  # 숏 청산은 buy
        print(f"\n🔵 숏 포지션 -> 최고점({high_price:.2f})에 스탑로스 설정")

    # 리스크 분석
    risk_analysis = analyze_position_risk(df, side, entry_price)
    if risk_analysis:
        print(f"\n📊 리스크 분석:")
        print(f"   현재가: {risk_analysis['current_price']:.2f}")
        print(f"   스탑로스: {risk_analysis['stop_loss_price']:.2f}")
        print(f"   리스크: {risk_analysis['distance_pct']:.2f}%")

    # 스탑로스 설정
    result = set_stop_loss(exchange, ccxt_symbol, stop_side, stop_price, size)

    if result:
        processed_positions.add(position_id)
        print(f"✅ {symbol} 스탑로스 설정 완료!\n")
    else:
        print(f"❌ {symbol} 스탑로스 설정 실패\n")


def is_symbol_watched(symbol, watch_symbols):
    """
    심볼이 감시 목록에 있는지 확인

    Args:
        symbol: 체크할 심볼 (예: 'BTCUSDT')
        watch_symbols: 감시 심볼 리스트 (None이면 모든 심볼 감시)

    Returns:
        bool: 감시 대상이면 True
    """
    if watch_symbols is None:
        return True  # 설정이 없으면 모든 심볼 감시

    # BTCUSDT, BTC/USDT:USDT 등 다양한 형식 처리
    symbol_clean = symbol.replace('/', '').replace(':', '')

    for watch_symbol in watch_symbols:
        watch_clean = watch_symbol.replace('/', '').replace(':', '')
        if symbol_clean == watch_clean:
            return True

    return False


def monitor_positions(exchange, check_interval, watch_symbols=None):
    """
    포지션 모니터링 루프

    Args:
        exchange: CCXT exchange 객체
        check_interval: 체크 간격 (초)
        watch_symbols: 감시할 심볼 리스트 (None이면 모든 심볼)
    """
    print("🚀 Bybit 자동 스탑로스 봇 시작")
    print(f"⏰ 포지션 체크 간격: {check_interval}초")

    if watch_symbols:
        print(f"👁️  감시 심볼: {', '.join(watch_symbols)}")
    else:
        print(f"👁️  감시 심볼: 모든 심볼")

    print()

    while True:
        try:
            # 현재 포지션 조회
            positions = get_positions(exchange)

            if positions:
                # 감시 대상 심볼만 필터링
                filtered_positions = [
                    pos for pos in positions
                    if is_symbol_watched(pos['symbol'], watch_symbols)
                ]

                if filtered_positions:
                    print(f"\n📍 [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                          f"활성 포지션: {len(positions)}개 "
                          f"(감시 대상: {len(filtered_positions)}개)")

                    for position in filtered_positions:
                        process_position(exchange, position)
            else:
                # 포지션이 없으면 추적 목록 초기화
                if processed_positions:
                    print(f"\n💤 모든 포지션이 청산되었습니다. 추적 목록 초기화.")
                    processed_positions.clear()

            # 대기
            time.sleep(check_interval)

        except KeyboardInterrupt:
            print("\n\n⛔ 프로그램 종료")
            break
        except Exception as e:
            print(f"\n❌ 오류 발생: {e}")
            time.sleep(check_interval)


def parse_watch_symbols():
    """
    환경 변수에서 감시 심볼 리스트 파싱

    Returns:
        list or None: 감시 심볼 리스트 (설정 없으면 None)
    """
    watch_symbols_str = os.getenv('WATCH_SYMBOLS', '').strip()

    if not watch_symbols_str:
        return None

    # 쉼표로 구분된 심볼 파싱
    symbols = [s.strip() for s in watch_symbols_str.split(',') if s.strip()]

    return symbols if symbols else None


def main():
    """메인 함수"""
    # Bybit 클라이언트 생성
    exchange = create_bybit_client()

    # 체크 간격 설정
    check_interval = int(os.getenv('CHECK_INTERVAL', '5'))

    # 감시 심볼 설정
    watch_symbols = parse_watch_symbols()

    # 모니터링 시작
    monitor_positions(exchange, check_interval, watch_symbols)


if __name__ == '__main__':
    main()
