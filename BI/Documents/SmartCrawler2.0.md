# I. Smart Crawler의 이해

###  1. Smart Crawler가 진단하려는 것
* '현재보다 더 자주' 크롤되어야 하는 것
* 이런 의미에서 현재 SC(이하에서 기술)는 적절지 않음

### 2. Smart Crawler(ver 2.0)가 실제 하는 것
* 1일 1회 이상 크롤되어야 한다고 진단된 아이템들을 EXECUTE_PLAN 테이블에 올린다.
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

### 4. 개발상의 난점
* ITEM 별로 크롤 주기가 불규칙하다.
  * 한 아이템이 심하면 1시간 ~ 1주일까지도 차이남: 이로 인해 해당 아이템에 대해 통계적 추정량을 산출하는 것이 어려움.
  * 각 아이템의 크롤간격이 상이하게 다름: 그렇게 되는 원인이 테이블 혹은 문서로 정리된 바 없음.
     * 물어봤을 때 없다고 들었지만 있다면 추가 바람
* 현재 크롤 중인 아이템을 명확하게 파악하기가 불가능: 명확한 지표가 전혀 없음
* STOCK_ID가 같지만 다른 출처인 경우: 마킹을 추가함
* 서버의 사망: 핵심 타겟이 GSSHOP인데, 개발 도중 크롤이 원활히 진행되지 않고 있다.
* 평가 지표 산출의 어려움: 임의의 시점 t에 대해 크롤링을 지시했을 때, t + 1~2분 뒤에 크롤된 자료가 입력된다.
  * 이 둘을 merge 하는 것이 기술적으로 가능은 하지만, 다소 시간과 개발 상의 번거로움이 있다.
* 병렬적인 크롤링 프로세스
  * SC로 지시한 크롤링이 도는 동시에 기존의 크롤 로직이 동작한다
  * 타겟을 1일 1회 이상 크롤해야하는 것으로 정의할 경우에, 해당 아이템이 현재 이미 1일 1회 크롤하고 있을 수도 있다.
* SC의 개발은 쉽지만 개발팀의 개발이 어렵다고 한 아이디어
  * '덜' 크롤해야 하는 것은 비교적 탐지하기 쉽다.
  * 하루에 2~3회 이상씩 긁지만 일주일 이상 재고량이 변하지 않는 ITEM 또한 다수 존재한다.
  * 그러나 이런 방향의 개발은 어렵다고 한다 ...

<br><br>
- - -
<br><br>


# II. SC 2.0 모델 로직

## Step 1

### 1. 현재 크롤 중으로 추정되는 ITEM들의 ID 가져오기 
  * retrieve_ids: 대상 사이트(ex. GSSHOP)로부터 최근 1주일간 업데이트(upt_dt)된 ID 목록을 가져온다.
  * ITEM_NUM을 가져오는 이유는 BS_URL 테이블과의 join을 위해서이다.
  * 개발 때에는 이곳에 limit을 건다
  * INPUT: None
  * OUTPUT: target_items
 
  
### 2. 판매종료되지 않은 ITEM들의 ITEM_NUM 가져오기
  * get_BS_URL_ids: BASE_URL 테이블의 SELL_END_YN을 토대로 판매종료되지 않은 상품의 ITEM_NUM을 가져온다.
  * SELL_END_YN을 완전히 신뢰할 수 없기 때문에 1에서 upt_dt를 참조하였다.
  * INPUT: None
  * OUTPUT: BS_URL
  
### 3. 판매종료된 상품 필터링
  * SELL_FILTER: ITEM_NUM을 토대로 SELL_END_YN이 0인 ITEM_ID만을 남겨 반환한다.
  * INPUT: target_items, BS_URL
  * OUTPUTL: target_item_ids  
  
### 4. Step2 triggering
  * 끝나는 동시에 SC step2를 작동시킨다.
  * step2에 대해서는 스케쥴링이 연 1회로 설정되어있다. 지우거나 파일이 존재할 때만 돌아가도록 설정해야할 것 같다.
  
## Step2

### 0. 파일 정리
  * organizing_files: 해당 주차에 크롤 타겟이었던 ITEM ID들은 current로 마킹되어있다. 이 파일이 존재한다면 이름에서 current를 제거한다.

### 1. 아이템 리스트 쪼개기
  * make_dic: 아이템리스들을 각 파티션별로, 그리고 파티션 내에서도 1000개 단위로 쪼개 dictionary 형태로 반환한다.
  * 파티션 단위로 쪼갰을 때는 하나의 chunk가 클 경우 bottleneck이 심각해질 수 있기 때문이다.
  * STEP2의 이하 작업들은 여기서 쪼개진 CHUNK 단위로 진행된다. 
  * INPUT: target_item_ids
  * OUTPUT: dic
  
### 2. 주어진 CHUNK에서 ITEM별로 최근 4주간의 재고량을 가져온다.
  * retrieve_from_presto: 파티션을 잘 이용해 가져온다.
    * item_part는 item_id에 따른 파티션, select_ids는 CHUNK에 담긴 ITEM들의 id다.
    * month 또한 partitioned columns이다.
  * INPUT: item_part, select_ids, today, last_month
  * OUTPUT: items_df

### 3. 재고량으로부터 Feature를 생성해 저장한다.
  * assecing: 파티션별로 재고량을 읽어 feature들을 생성한 뒤 저장한다.
  * feature는 reposit/SmartCrawler/site_hive/Featuress에 피클로 저장된다.
    * ex) /app/dev/airflow/reposit/SmartCrawler/GSSHOP/Features/123
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
  * INPUT: items_df, item_part

### 4. 더 크롤해야 할 ITEM 예측
  * predict_from_features: 생성된 feature로부터 더 크롤해야 할 ITEM을 예측하여 반환
  * reporting을 위해 총 ITEM의 수(total_len)을 반환한다.
  * First layer: 다음의 모델들을 활용해 meta predictor 생성
    * Ada_Logit: Logistic regression
    * Ada_Tree: Tree
    * LDA: Linear discriminent analysis
    * RF: Random forest
  * Second layer: meta predictor로부터 더 크롤할 ITEM들 classify하여 저장
  * INPUT: features
  * OUTPUT: total_len, predicted_ids

### 5. 결과 레포팅
  * reporting_SC_predict_done: 프로세스가 진행된 사이트의 이름, 아이템의 수 등을 텔레그램으로 보내준다.
  * INPUT: site_hive, predicted_len, total_len, randomly_len


### 6. 더 크롤할 ITEM 저장
  * aggregating_features: 예측된 ITEM과 그 대조군을 종합하여 반환
  * rest_ids: 현재 크롤이 진행되는 ITEM에서 더 크롤이 필요하다고 판단되지 않는 아이템들 중 일부를 임의추출
  * predicted_id에는 SC=True, randomly sampled에는 SC=False로 마킹
  * 총 5만개중 predictied_id를 채우고 나머지를 random sample로 채울 예정
    * 10/30 현재 GSSHOP의 크롤이 원활히 진행되고 있지 않기 때문에 predicted_id의 개수만큼만 random sample할 예정
  * EXECUTE_PLAN에 넣기 위해 ITEM_NUM을 붙여서 진행
  * 최종적으로 ITEM들은 reposit/SmartCrawler/site_hive/CrawledItems에 날짜와 함께 피클로 박제된다.
  * 아이템이 박제될 때는 current로 마킹이 되며, 크롤 기간이 끝난 아이템은 파일 이름에서 current만 

## 7. 임시 파일 제거
  * feature들을 모두 제거
  
<br><br>
- - - 
<br><br>

## III. 예측 모델 생성
