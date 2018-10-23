## Smart Crawler의 이해

###  1. Smart Crawler가 진단하려는 것
* '현재보다 더 자주' 크롤되어야 하는 것
* 이런 의미에서 현재 SC(이하에서 기술)는 적절지 않음

### 2. Smart Crawler가 실제 하는 것
* 더 자주 크롤되어야 한다고 진단된 아이템들을 EXECUTE_PLAN 테이블에 올린다.
  * 현재 얼마나 자주 크롤되고 있는지는 고려하지 않는다.
  * 현재 크롤 주기가 짧을 때 정보량이 더 많기는 하다.
* 어떤 아이템을(ITEM_NUM) 언제(ACT_DT) 어디서(COLLECT_SITE) 크롤할 것인지를 등록(REG_DT).
  * queuing_execute_plan.py을 참조 (git)
  * pandas가 지원하는 rolling이나 data_range 함수가 유용하다.
* EXECUTE_PLAN에 큐를 넣을 때는 개발팀에 미리 말을 **꼭!!** 해야 한다.
  * Default로는 꺼져있다.

### 3. 부차적인 문제
* 크롤이 종료된 아이템을 EXECUTE_PLAN에 넣으면 좋지 않다
  * 잘못되면 크롤링 전체가 fail될 수 있다. 이를 검증하기 위해 BS_URL의 SELL_END_YN 칼럼을 참조하지만 신뢰도 검토중.
  
