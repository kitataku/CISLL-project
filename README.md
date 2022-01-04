# CISLL-project

## bots

### Bollinger Band

逆張りボリンジャーバンドによる売買判断を行う。

### ADX(Average Directional Movement Index)

ADXによる売買判断を行う。

#### 買い判断

以下のすべてを満たすときに買い判断を行う。

- +DIが-DIを下から上に突き抜ける
- ADXが上昇
- +DI > ADX > -DI

#### 売り判断

以下のすべてを満たすときに売り判断を行う。

- -DIが+DIを下から上に突き抜ける
- ADXが上昇
- -DI > ADX > +DI

### A2C

