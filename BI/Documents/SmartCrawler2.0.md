## Smart Crawler의 이해

###  1. Smart Crawler가 진단하려는 것
* '현재보다 더 자주' 크롤되어야 하는 것
* 이런 의미에서 현재 SC(이하에서 기술)는 적절지 않음

### 2. Smart Crawler(ver 2.0)가 실제 하는 것
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


<br><br>
- - -
<br><br>


## SC 2.0 모델 로직

### 1. 현재 크롤 중으로 추정되는 ITEM들의 ID 가져오기 
  * retrieve_ids: 대상 사이트(ex. GSSHOP)로부터 최근 1주일간 업데이트(upt_dt)된 ID 목록을 가져온다.
  * ITEM_NUM을 가져오는 이유는 BS_URL 테이블과의 join을 위해서이다.
  * INPUT: None
  * OUTPUT: target_items
  * 소요시간: 10초 미만
  
### 2. 판매종료되지 않은 ITEM들의 ITEM_NUM 가져오기
  * get_BS_URL_ids: BASE_URL 테이블의 SELL_END_YN을 토대로 판매종료되지 않은 상품의 ITEM_NUM을 가져온다.
  * SELL_END_YN을 완전히 신뢰할 수 없기 때문에 1에서 upt_dt를 참조하였다.
  * INPUT: None
  * OUTPUT: BS_URL
  
### 3. 판매종료된 상품 필터링
  * SELL_FILTER: ITEM_NUM을 토대로 SELL_END_YN이 0인 ITEM_ID만을 남겨 반환한다.
  * INPUT: target_items, BS_URL
  * OUTPUTL: target_item_ids

### 4. 재고량 가져오기
  * pulling_items: 파티션 별로 최근 4주간의 재고량을 가져와 저장한다.
  * 재고량은 파티션 별로 reposit/SC_stocks에 날짜(연월일)와 함께 피클로 저장된다.
    * ex) reposit/SC_stocks/20181101_123.pk
  * 저장된 디렉토리를 반환한다.
  * INPUT: target_item_ids
  * OUTPUT: stock_direc

### 5. 재고량으로부터 Feature를 생성한다.
  * assecing: 파티션별로 재고량을 읽어 feature들을 생성한 뒤 저장한다.
  * feature는 reposit/SC_features에 날짜(연월일)과 함께 피클로 저장된다.
    * ex) reposit/SC_stocks/20181101_123.pk
  * 내부에서 호출하는 함수들은 다음과 같다
    * modify_1sec: 아이템 별로 크롤 간격에 대한 전처리를 수행한다. HowToCrawl 3번 참조
    * get_weighed_r_from_df: 아이템 하나에 대한 R-score를 구한다. 주별로 가중치가 1/e로 감소한다.
    * r_byweek: 주별로 R_score를 구한다.  
      -period는 단위기간을 가리킨다.  
      -n=len(resampled)로 설정할 경우 관측 횟수가 적은 경우에 편향이 생길 수 있다.  
      -weight는 경험적으로 주어졌다. 현재의 weight=1.5를 토대로, R-score는 1.5가 적절하다고 보인다.  
    * caclulate_r: 연속성 수정과 함께 r값을 계산한다.  
  * 생성한 feature는 다음과 같다.
    * CRAWL: 크롤한 횟수. modify_1sec가 없으면 과대추정된다.
    * CHANGE: 크롤했을 때 재고가 변화한 횟수. CRAWL보다 항상 작거나 같다.
    * CHANGED_DAY: 크롤했을 때 재고가 변화한 날짜. CHANGE보다 항상 작거나 같다.
    * PERIOD: 크롤해온 기간. 중간에 안한 기간을 참고하지 않기 때문에 과다추정될 수 있다.
    * CATCH_RATE: CHANGE/CRAWL. 크롤횟수 대비 재고량변화횟수이다.
    * LAST_STOCK_IS_ZERO: 가장 마지막에 크롤됐을 때의 재고량.
    * N_STOCK: STOCK의 가짓수이다.
  * INPUT: stock_direc
  * OUTPUT: feature_direc
