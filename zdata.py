from rqdatac import *
import pandas as pd
import numpy as np
import datetime
import tushare as ts

class Stock_indicators_tushare():
    
    def __init__(self,stock_code,**kwargs):
#         self.SMA=None
        stock_code=str(stock_code)
        stock_code=stock_code[:6]
        
        today=datetime.date.today()
        half_year_before=today-datetime.timedelta(days=182)
        if 'start' in kwargs.keys():
            half_year_before=kwargs['start']
        if 'end' in kwargs.keys():
            today=kwargs['start']
            
        #real_daily=get_price(stock_code, half_year_before, end_date=today, frequency='1d' )
        real_daily=ts.get_hist_data(stock_code,half_year_before,end=today)
        real_daily=real_daily[::-1]
        r=real_daily.copy()
        
        SMA=r['close'].rolling(10).mean()
        SMA=SMA.rename('SMA')
        r.insert(0,'SMA10',SMA)
        self.SMA=SMA

        window=list(np.linspace(1,10,num=10))
        WMA=real_daily['close'].rolling(win_type='boxcar',window=window,axis=0).mean()
        WMA=WMA.rename('WMA')
        r.insert(0,'WMA',WMA)
        self.WMA=WMA


        window=[-1,0,0,0,0,0,0,0,0,1]
        MOM=real_daily['close'].rolling(win_type='boxcar',window=window,axis=0).sum()   
        MOM=MOM.rename('MOM')
        r.insert(0,'MOM',MOM)
        self.MOM=MOM


        y=r[['close','high','low']].copy()
        hh=y.high.rolling(window=10).max()
        ll=y.low.rolling(window=10).min()
        temp=pd.DataFrame(y.close).join(hh).join(ll)
        temp.columns=['close', 'highest_high', 'lowest_low']
        Stok=100*((temp.close-temp.lowest_low)/(temp.highest_high-temp.lowest_low))
        Stok=pd.DataFrame(Stok)
        Stok.columns=['Sto_k']
        temp=temp.join(Stok)
        r.insert(0,'Sto_k',temp.Sto_k)
        self.Sto_k=temp.Sto_k


        temp=r.Sto_k.rolling(window=10).mean()
        temp=temp.rename('Sto_d')
        r.insert(0,'Sto_d',temp)
        self.Sto_d=temp



        delta=r.close.diff()
        UP,DW=delta.copy(),delta.copy()
        UP[UP<0]=0
        DW[DW>0]=0
        DW=abs(DW)
        up=UP.rolling(10).sum()
        up=up.rename('up')
        dw=DW.rolling(10).sum()
        dw=dw.rename('dw')
        rs=up/dw
        RSI=rs.apply(lambda x : 100-100/(1+x))
        RSI=RSI.rename('RSI')
        r.insert(0,'RSI',RSI)
        self.RSI=RSI




        def ema_zl(self,dataframeseries,com=12,window=132,**kwargs):
            if 'alpha' in kwargs.keys():
                com=(1/kwargs['alpha']) -1
                com=int(com)
            temp=dataframeseries.copy() # prevent dataframeseries from changing
            data_be_cal=temp[-window:]
            start_base=data_be_cal[:com].mean()
            data_be_cal=data_be_cal[com-1:]
            data_be_cal.iloc[0]=start_base
            data_be_cal=data_be_cal.ewm(com=com,adjust=0).mean()
            data_be_cal=data_be_cal.rename(data_be_cal.name+'_ema'+str(com))
            return data_be_cal
        self.ema_zl=ema_zl

        def macd_zl(self,x):
            macd=(ema_zl(self,x,com=12)-ema_zl(self,x,com=26))
            macd=macd.rename('MACD')
            return macd
        self.macd_zl=macd_zl



        def signal_line_zl(self,x):
            MACD=macd_zl(x)
            sig_line=ema_zl(self,MACD,com=9).rename('signal_line')
            return sig_line
        self.signal_line_zl=signal_line_zl


        def macd_histogram_zl(self,x):
            return (macd_zl(self,x)-signal_line_zl(self,x)).rename('macd_histogram')
        self.macd_histogram_zl=macd_histogram_zl

        MACD=macd_zl(self,r.close)
        MACD=MACD.rename('MACD')
        r.insert(0,'MACD',MACD)
        self.MACD=MACD


        w_c=r['close']
        w_h=r['high'].rolling(window=14).max().rename('high_high')
        w_l=r['low'].rolling(window=14).min().rename('low_low')
        wr=((w_h-w_c)/(w_h-w_l))*(-100)
        wr=wr.rename('Willi_R')
        r.insert(0,'Willi_R',wr)
        self.wr=wr


        ad=r[['high','low']].join(r['close'].shift(1).rename('close_yestoday'))
        ad=((ad['high']-ad['close_yestoday']))/((ad['high']-ad['low']))
        ad=ad.rename('AD')
        r.insert(0,'AD',ad)
        self.ad=ad


        cci=r[['high','low','close']].copy()
        M=(cci['high']+cci['low']+cci['close'])/3
        M=M.rename('M')
        SM=M.rolling(14).mean()
        SM=SM.rename('SM')
        tr=pd.DataFrame([M,SM]).T.copy()
        li_st=list(tr['SM'].dropna().values)
        li_st=li_st[::-1]
        len(li_st)
        def abs_sum_mean(self,rolling):
            temp=li_st.pop()
        #     print(temp)
            lenth=len([i for i in rolling])
            return sum( abs(temp-i) for i in rolling)/lenth

        CCI=tr['M'].rolling(14).apply(lambda x : abs_sum_mean(self,x))
        CCI=CCI.rename('CCI')
        r.insert(0,'CCI',CCI)
        self.CCI=CCI
        
        r=r.dropna()
        self.indicators=r
        self.close=real_daily['close']
        self.open=real_daily['open']
        self.high=real_daily['high']
        self.low=real_daily['low']
        self.volume=real_daily['volume']




class Stock_indicators():
    
    def __init__(self,stock_code,**kwargs):
#         self.SMA=None
        
        
        today=datetime.date.today()
        half_year_before=today-datetime.timedelta(days=182)
        frequency='1d'
        if 'start' in kwargs.keys():
            half_year_before=kwargs['start']
        if 'end' in kwargs.keys():
            today=kwargs['start']
        if 'frequency' in kwargs.keys():
             frequency=kwargs['frequency']
            
        #real_daily=get_price(stock_code, half_year_before, end_date=today, frequency='1d' )
        #print(half_year_before)
        real_daily=get_price(str(stock_code),half_year_before,end_date=today,frequency=frequency)
        #real_daily=real_daily[::-1]
        r=real_daily.copy()
        
        SMA=r['close'].rolling(10).mean()
        SMA=SMA.rename('SMA')
        r.insert(0,'SMA10',SMA)
        self.SMA=SMA

        window=list(np.linspace(1,10,num=10))
        WMA=real_daily['close'].rolling(win_type='boxcar',window=window,axis=0).mean()
        WMA=WMA.rename('WMA')
        r.insert(0,'WMA',WMA)
        self.WMA=WMA


        window=[-1,0,0,0,0,0,0,0,0,1]
        MOM=real_daily['close'].rolling(win_type='boxcar',window=window,axis=0).sum()   
        MOM=MOM.rename('MOM')
        r.insert(0,'MOM',MOM)
        self.MOM=MOM


        y=r[['close','high','low']].copy()
        hh=y.high.rolling(window=10).max()
        ll=y.low.rolling(window=10).min()
        temp=pd.DataFrame(y.close).join(hh).join(ll)
        temp.columns=['close', 'highest_high', 'lowest_low']
        Stok=100*((temp.close-temp.lowest_low)/(temp.highest_high-temp.lowest_low))
        Stok=pd.DataFrame(Stok)
        Stok.columns=['Sto_k']
        temp=temp.join(Stok)
        r.insert(0,'Sto_k',temp.Sto_k)
        self.Sto_k=temp.Sto_k


        temp=r.Sto_k.rolling(window=10).mean()
        temp=temp.rename('Sto_d')
        r.insert(0,'Sto_d',temp)
        self.Sto_d=temp



        delta=r.close.diff()
        UP,DW=delta.copy(),delta.copy()
        UP[UP<0]=0
        DW[DW>0]=0
        DW=abs(DW)
        up=UP.rolling(10).sum()
        up=up.rename('up')
        dw=DW.rolling(10).sum()
        dw=dw.rename('dw')
        rs=up/dw
        RSI=rs.apply(lambda x : 100-100/(1+x))
        RSI=RSI.rename('RSI')
        r.insert(0,'RSI',RSI)
        self.RSI=RSI




        def ema_zl(self,dataframeseries,com=12,window=132,**kwargs):
            if 'alpha' in kwargs.keys():
                com=(1/kwargs['alpha']) -1
                com=int(com)
            temp=dataframeseries.copy() # prevent dataframeseries from changing
            data_be_cal=temp[-window:]
            start_base=data_be_cal[:com].mean()
            data_be_cal=data_be_cal[com-1:]
            data_be_cal.iloc[0]=start_base
            data_be_cal=data_be_cal.ewm(com=com,adjust=0).mean()
            data_be_cal=data_be_cal.rename(data_be_cal.name+'_ema'+str(com))
            return data_be_cal
        self.ema_zl=ema_zl

        def macd_zl(self,x):
            macd=(ema_zl(self,x,com=12)-ema_zl(self,x,com=26))
            macd=macd.rename('MACD')
            return macd
        self.macd_zl=macd_zl



        def signal_line_zl(self,x):
            MACD=macd_zl(x)
            sig_line=ema_zl(self,MACD,com=9).rename('signal_line')
            return sig_line
        self.signal_line_zl=signal_line_zl


        def macd_histogram_zl(self,x):
            return (macd_zl(self,x)-signal_line_zl(self,x)).rename('macd_histogram')
        self.macd_histogram_zl=macd_histogram_zl

        MACD=macd_zl(self,r.close)
        MACD=MACD.rename('MACD')
        r.insert(0,'MACD',MACD)
        self.MACD=MACD


        w_c=r['close']
        w_h=r['high'].rolling(window=14).max().rename('high_high')
        w_l=r['low'].rolling(window=14).min().rename('low_low')
        wr=((w_h-w_c)/(w_h-w_l))*(-100)
        wr=wr.rename('Willi_R')
        r.insert(0,'Willi_R',wr)
        self.wr=wr


        ad=r[['high','low']].join(r['close'].shift(1).rename('close_yestoday'))
        ad=((ad['high']-ad['close_yestoday']))/((ad['high']-ad['low']))
        ad=ad.rename('AD')
        r.insert(0,'AD',ad)
        self.ad=ad


        cci=r[['high','low','close']].copy()
        M=(cci['high']+cci['low']+cci['close'])/3
        M=M.rename('M')
        SM=M.rolling(14).mean()
        SM=SM.rename('SM')
        tr=pd.DataFrame([M,SM]).T.copy()
        li_st=list(tr['SM'].dropna().values)
        li_st=li_st[::-1]
        len(li_st)
        def abs_sum_mean(self,rolling):
            temp=li_st.pop()
        #     print(temp)
            lenth=len([i for i in rolling])
            return sum( abs(temp-i) for i in rolling)/lenth

        CCI=tr['M'].rolling(14).apply(lambda x : abs_sum_mean(self,x))
        CCI=CCI.rename('CCI')
        r.insert(0,'CCI',CCI)
        self.CCI=CCI
        
        r=r.dropna()
        self.indicators=r
        self.close=real_daily['close']
        self.open=real_daily['open']
        self.high=real_daily['high']
        self.low=real_daily['low']
        self.volume=real_daily['volume']


class Stock_indicators_x():
    
    def __init__(self,stock_code,**kwargs):
#         self.SMA=None
        
        
        today=datetime.datetime.strptime(str(datetime.date.today()),"%Y-%m-%d")
        half_year_before=datetime.datetime.strptime(str(today-datetime.timedelta(days=182))[:10],"%Y-%m-%d")
#         half_year_before=half_year_before.isoformat()
#         today=today.isoformat()
        frequency='1d'
        if 'start' in kwargs.keys():
            half_year_before=datetime.datetime.strptime(kwargs['start'],"%Y-%m-%d")
#             half_year_before=half_year_before.isoformat()
#             x1=datetime.datetime.strptime(kwargs['start'],"%Y-%m-%d")  
        if 'end' in kwargs.keys():
            today=datetime.datetime.strptime(kwargs['end'],"%Y-%m-%d")
#             today=today.isoformat()
            #x2=datetime.datetime.strptime(kwargs['end'],"%Y-%m-%d")
        if 'frequency' in kwargs.keys():
            frequency=kwargs['frequency']
        
#         try:
#             window=today-half_year_before
#         except:
        window_days=today-half_year_before
        window_days=window_days.days
        #real_daily=get_price(stock_code, half_year_before, end_date=today, frequency='1d' )
        #print(half_year_before)
        real_daily=get_price(str(stock_code),half_year_before,end_date=today,frequency=frequency)
        #real_daily=real_daily[::-1]
        r=real_daily.copy()
        
        SMA=r['close'].rolling(10).mean()
        SMA=SMA.rename('SMA')
        r.insert(0,'SMA10',SMA)
        self.SMA=SMA

        window=list(np.linspace(1,10,num=10))
        WMA=real_daily['close'].rolling(win_type='boxcar',window=window,axis=0).mean()
        WMA=WMA.rename('WMA')
        r.insert(0,'WMA',WMA)
        self.WMA=WMA


        window=[-1,0,0,0,0,0,0,0,0,1]
        MOM=real_daily['close'].rolling(win_type='boxcar',window=window,axis=0).sum()   
        MOM=MOM.rename('MOM')
        r.insert(0,'MOM',MOM)
        self.MOM=MOM


        y=r[['close','high','low']].copy()
        hh=y.high.rolling(window=10).max()
        ll=y.low.rolling(window=10).min()
        temp=pd.DataFrame(y.close).join(hh).join(ll)
        temp.columns=['close', 'highest_high', 'lowest_low']
        Stok=100*((temp.close-temp.lowest_low)/(temp.highest_high-temp.lowest_low))
        Stok=pd.DataFrame(Stok)
        Stok.columns=['Sto_k']
        temp=temp.join(Stok)
        r.insert(0,'Sto_k',temp.Sto_k)
        self.Sto_k=temp.Sto_k


        temp1=r.Sto_k.rolling(window=10).mean()
        temp1=temp1.rename('Sto_d')
        r.insert(0,'Sto_d',temp1)
        self.Sto_d=temp



        delta=r.close.diff()
        UP,DW=delta.copy(),delta.copy()
        UP[UP<0]=0
        DW[DW>0]=0
        DW=abs(DW)
        up=UP.rolling(10).sum()
        up=up.rename('up')
        dw=DW.rolling(10).sum()
        dw=dw.rename('dw')
        rs=up/dw
        RSI=rs.apply(lambda x : 100-100/(1+x))
        RSI=RSI.rename('RSI')
        r.insert(0,'RSI',RSI)
        self.RSI=RSI




        def ema_zl(dataframeseries,com=12,window=window_days,**kwargs):
            if 'alpha' in kwargs.keys():
                com=(1/kwargs['alpha']) -1
                com=int(com)
            temp=dataframeseries.copy() # prevent dataframeseries from changing
#             print(window)
            data_be_cal=temp[-window:]
            start_base=data_be_cal[:com].mean()
            data_be_cal=data_be_cal[com-1:]
            data_be_cal.iloc[0]=start_base
            data_be_cal=data_be_cal.ewm(com=com,adjust=0).mean()
            data_be_cal=data_be_cal.rename(data_be_cal.name+'_ema'+str(com))
            return data_be_cal
        self.ema_zl=ema_zl

        def macd_zl(x):
            macd=(ema_zl(x,com=12)-ema_zl(x,com=26))
            macd=macd.rename('MACD')
            return macd
        self.macd_zl=macd_zl



        def signal_line_zl(x):
            MACD=macd_zl(x)
            sig_line=ema_zl(MACD,com=9).rename('signal_line')
            return sig_line
        self.signal_line_zl=signal_line_zl


        def macd_histogram_zl(x):
            return (macd_zl(x)-signal_line_zl(x)).rename('macd_histogram')
        self.macd_histogram_zl=macd_histogram_zl

        MACD=macd_zl(r.close)
        MACD=MACD.rename('MACD')
        r.insert(0,'MACD',MACD)
        self.MACD=MACD


        w_c=r['close']
        w_h=r['high'].rolling(window=14).max().rename('high_high')
        w_l=r['low'].rolling(window=14).min().rename('low_low')
        wr=((w_h-w_c)/(w_h-w_l))*(-100)
        wr=wr.rename('Willi_R')
        r.insert(0,'Willi_R',wr)
        self.wr=wr


        ad=r[['high','low']].join(r['close'].shift(1).rename('close_yestoday'))
        ad=((ad['high']-ad['close_yestoday']))/((ad['high']-ad['low']))
        ad=ad.rename('AD')
        r.insert(0,'AD',ad)
        self.AD=ad


        cci=r[['high','low','close']].copy()
        M=(cci['high']+cci['low']+cci['close'])/3
        M=M.rename('M')
        SM=M.rolling(14).mean()
        SM=SM.rename('SM')
        tr=pd.DataFrame([M,SM]).T.copy()
        li_st=list(tr['SM'].dropna().values)
        li_st=li_st[::-1]
        len(li_st)
        def abs_sum_mean(rolling):
            temp=li_st.pop()
        #     print(temp)
            lenth=len([i for i in rolling])
            return sum( abs(temp-i) for i in rolling)/lenth

        D=tr['M'].rolling(14).apply(lambda x : abs_sum_mean(x))
        CCI=(M-SM)/(0.015*D)

        CCI=CCI.rename('CCI')
        r.insert(0,'CCI',CCI)
        self.CCI=CCI
        
        self.ori_indicators=r
        r=r.dropna()
        self.indicators=r
        self.close=real_daily['close']
        self.open=real_daily['open']
        self.high=real_daily['high']
        self.low=real_daily['low']
        self.volume=real_daily['volume']