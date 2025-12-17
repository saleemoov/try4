#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار شامل لنظام ICT المتقدم
Test Complete ICT System
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from advanced_trading_bot import ICTAnalyzer, TechnicalAnalyzer

def generate_test_data():
    """توليد بيانات اختبار واقعية"""
    # إنشاء 100 شمعة تجريبية
    dates = pd.date_range(start='2024-12-01', periods=100, freq='15min')
    
    # بيانات مع توحيد و breakout
    np.random.seed(42)
    base_price = 0.0003
    
    close = []
    high = []
    low = []
    volume = []
    
    price = base_price
    
    for i in range(100):
        # توحيد في الشموع 40-60
        if 40 <= i <= 60:
            # سعر مستقر
            change = np.random.randn() * 0.00001
            volume_val = 1000000 + np.random.randn() * 100000
        # كسر صاعد في الشموع 70+
        elif i > 70:
            change = abs(np.random.randn() * 0.00002)  # صعود قوي
            volume_val = 5000000 + np.random.randn() * 500000  # حجم مرتفع
        else:
            change = np.random.randn() * 0.00001
            volume_val = 1500000 + np.random.randn() * 200000
        
        price += change
        close.append(price)
        high.append(price + abs(np.random.randn() * 0.00001))
        low.append(price - abs(np.random.randn() * 0.00001))
        volume.append(max(100000, volume_val))
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': close,
        'high': high,
        'low': low,
        'close': close,
        'volume': volume
    })
    
    df = df.set_index('timestamp')
    return df

def test_ict_analyzer():
    """اختبار محلل ICT"""
    print("\n" + "="*70)
    print("🧪 اختبار محلل ICT")
    print("="*70)
    
    df = generate_test_data()
    print(f"\n✅ تم توليد {len(df)} شمعة اختبار")
    print(f"   السعر الأول: ${df['close'].iloc[0]:.8f}")
    print(f"   السعر الحالي: ${df['close'].iloc[-1]:.8f}")
    print(f"   أعلى: ${df['high'].max():.8f}")
    print(f"   أقل: ${df['low'].min():.8f}")
    
    analyzer = ICTAnalyzer()
    ict_analysis = analyzer.analyze_ict(df, "TEST/USDT")
    
    print("\n📊 نتائج تحليل ICT:")
    
    # Order Blocks
    print("\n🎯 Order Blocks:")
    if ict_analysis['order_blocks']['buy_blocks']:
        print(f"   ✅ عدد مناطق الشراء: {len(ict_analysis['order_blocks']['buy_blocks'])}")
        for block in ict_analysis['order_blocks']['buy_blocks'][-2:]:
            print(f"      - نطاق: ${block['low']:.8f} - ${block['high']:.8f} (قوة: {block['strength']:.2f}x)")
    
    if ict_analysis['order_blocks']['nearest_buy']:
        print(f"   🟢 Order Block نشط (شراء): ${ict_analysis['order_blocks']['nearest_buy']['low']:.8f} - ${ict_analysis['order_blocks']['nearest_buy']['high']:.8f}")
    
    # Fair Value Gaps
    print("\n💰 Fair Value Gaps:")
    if ict_analysis['fair_value_gaps']['bullish_fvgs']:
        print(f"   ✅ عدد الفراغات الصاعدة: {len(ict_analysis['fair_value_gaps']['bullish_fvgs'])}")
        for fvg in ict_analysis['fair_value_gaps']['bullish_fvgs'][-2:]:
            print(f"      - حجم: ${fvg['size']:.8f} ({fvg['bars_ago']} شموع)")
    
    if ict_analysis['fair_value_gaps']['active_fvg']:
        fvg = ict_analysis['fair_value_gaps']['active_fvg']
        print(f"   🟢 FVG نشط ({fvg['type']}): ${fvg['bottom']:.8f} - ${fvg['top']:.8f}")
    
    # Liquidity Zones
    print("\n🌊 Liquidity Zones:")
    if ict_analysis['liquidity_zones']['demand_zones']:
        print(f"   ✅ عدد مناطق الطلب: {len(ict_analysis['liquidity_zones']['demand_zones'])}")
        for zone in ict_analysis['liquidity_zones']['demand_zones'][-2:]:
            print(f"      - مستوى: ${zone['level']:.8f} (قوة: {zone['strength']} شموع)")
    
    if ict_analysis['liquidity_zones']['active_zone']:
        zone = ict_analysis['liquidity_zones']['active_zone']
        print(f"   🟢 Demand Zone نشطة: ${zone['level']:.8f} (قوة: {zone['strength']})")
    
    # Supply/Demand
    print("\n📊 Supply & Demand:")
    sd = ict_analysis['supply_demand']
    print(f"   شراء: ${sd['volume_buy']:,.0f}")
    print(f"   بيع: ${sd['volume_sell']:,.0f}")
    print(f"   عدم التوازن: {sd['imbalance']*100:.1f}%")
    
    # الإشارة النهائية
    print("\n🎬 الإشارة النهائية:")
    print(f"   الإشارة: {ict_analysis['ict_signal']}")
    print(f"   القوة: {ict_analysis['ict_strength']:.1f}%")
    
    return ict_analysis

def test_technical_analyzer():
    """اختبار محلل التحليل الفني"""
    print("\n" + "="*70)
    print("🧪 اختبار محلل التحليل الفني + ICT")
    print("="*70)
    
    df = generate_test_data()
    
    analyzer = TechnicalAnalyzer()
    analysis = analyzer.analyze_candles(df, "TEST/USDT")
    
    if not analysis:
        print("❌ فشل التحليل")
        return
    
    print("\n📊 نتائج التحليل الفني:")
    
    # EMA
    print("\n📈 EMA:")
    print(f"   EMA5: ${analysis['ema']['ema5']:.8f}")
    print(f"   EMA8: ${analysis['ema']['ema8']:.8f}")
    print(f"   EMA13: ${analysis['ema']['ema13']:.8f}")
    print(f"   الحالة: {analysis['ema']['status']}")
    
    # RSI
    print("\n📊 RSI:")
    print(f"   القيمة: {analysis['rsi']['value']:.1f}")
    print(f"   الحالة: {analysis['rsi']['condition']}")
    
    # MACD
    print("\n🎯 MACD:")
    print(f"   القيمة: {analysis['macd']['macd']:.8f}")
    print(f"   الإشارة: {analysis['macd']['signal']:.8f}")
    print(f"   الحالة: {analysis['macd']['condition']}")
    
    # التوحيد
    print("\n🔎 منطقة التوحيد:")
    cons = analysis['consolidation']
    print(f"   توحيد: {cons['is_consolidating']}")
    print(f"   القوة: {cons['strength']:.1f}/100")
    print(f"   النطاق: ${cons['low']:.8f} - ${cons['high']:.8f}")
    print(f"   حجم النطاق: {cons['range_pct']*100:.2f}%")
    
    # ICT
    print("\n🎯 تحليل ICT:")
    ict = analysis.get('ict', {})
    if ict:
        print(f"   الإشارة: {ict['ict_signal']}")
        print(f"   القوة: {ict['ict_strength']:.1f}%")
    
    return analysis

def test_signal_generation():
    """اختبار توليد الإشارات"""
    print("\n" + "="*70)
    print("🧪 اختبار توليد الإشارات")
    print("="*70)
    
    # تحليل الدخول (15m)
    df_entry = generate_test_data()
    
    # تحليل الاتجاه (4H)
    df_trend = generate_test_data()[::4].copy()  # تقليل العينات
    
    analyzer = TechnicalAnalyzer()
    entry_analysis = analyzer.analyze_candles(df_entry, "TEST/USDT")
    trend_analysis = analyzer.analyze_candles(df_trend, "TEST/USDT")
    
    signal, strength, details = analyzer.generate_trading_signal(entry_analysis, trend_analysis)
    
    print("\n🎬 الإشارة المولدة:")
    print(f"   نوع الإشارة: {signal}")
    print(f"   قوة الإشارة: {strength:.1f}%")
    
    print("\n📝 التفاصيل:")
    for i, detail in enumerate(details, 1):
        print(f"   {i}. {detail}")
    
    return signal, strength, details

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🚀 اختبار نظام ICT المتقدم الشامل")
    print("="*70)
    
    try:
        # 1. اختبار ICT
        ict_result = test_ict_analyzer()
        
        # 2. اختبار التحليل الفني
        tech_result = test_technical_analyzer()
        
        # 3. اختبار توليد الإشارات
        signal_result = test_signal_generation()
        
        print("\n" + "="*70)
        print("✅ جميع الاختبارات نجحت!")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        import traceback
        traceback.print_exc()
