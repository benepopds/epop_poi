# SC_daily_queuing
## SC가 예측한 아이템들을 매일 EXECUTE_PLAN으로 queuing
### 1. Queuing
* 매일 아침 9시에 작동
* SC가 예측한 아이템을 11개로 쪼개 11시부터 한시간 간격으로 넣어준다
* IP에 의해 크롤되는 아이템은 매일매일 확인해 제거한다.

### 2. Reporting
  * 위의 작업들은 telegram으로 레포팅된다.
  * 어느 사이트에서 몇 개의 아이템이 
