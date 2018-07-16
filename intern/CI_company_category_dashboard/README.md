# CI TEMP_COMPANY TABLE CATEGORY DASHBOARD  
  
  
## 사용하는 DB    
  
*Read :*  
  
133.186.146.142:3306/eums-poi 에 있는 MEUMS_COMPANY 의 Copy 본인 TEMP_COMPANY    
(즉, TEMP_COMPANY 에 DB가 변경되지만 MEUMS_COMPANY 의 실제 DB는 변경되지 않음. 테스트가 충분하다면 변경해야함.)    
  
133.186.146.142:3306/eums-poi 에 있는 MEUMS_CODE 테이블  
  
*Write :* 
  
133.186.146.142:3306/eums-poi 에 있는 TEMP_COMPANY_EXCLUDE_HISTORY (status -9 처리 하는 로그 기록)  
  
133.186.146.142:3306/eums-poi 에 있는 TEMP_COMPANY_UPDATE_HISTORY (DB 변경한 로그 기록)  
  
  
## 기능  
  
  
  
  
![Alt text](img/main.png)  
  
  
  
상점 이름에 있는 pair 를 보고 카테고리를 정제할 수 있다.  
각 pair 별로 가장 많은 CATE, CATE1 순서로 출력하여 보여준다.  
default 로 가장 많은 수의 CATE, CATE1 값이 MODIFY 버튼 옆에 적혀잇지만  
다른 카테고리로 직접 입력하여 CATE, CATE1 값을 변경할 수 있다.  
  
결제를 할 수 없는 특정 상점을 보게 된다면 해당 항목을 선택한 후 상점찾기 제외 버튼을 누르면  
STATUS 가 -9 로 변경된다. 그 후 로그가 자동으로 TEMP_COMPANY_EXCLUDE_HISTORY로 기록된다.  
  
MODIFY 버튼을 클릭하면 위에서 입력한 CATE, CATE1 로 변경되며 자동으로  
TEMP_COMPANY_UPDATE_HISTORY에 기록된다.  
  
SYNC DB-PQ 버튼을 클릭하게 된다면 실제 DB값대로 PQ 파일이 업데이트 된다.  
이 과정은 꽤 오랜 시간이 걸린다.  
  
LOGIN 기능이 있다. 이는 오픈소스인 DASH-AUTH 를 수정하여 적용하였다.  

ID 는 admin1, admin2, admin3 이며  
비밀번호는 epop0313 이다.  
  
## 주의사항  
  
충분한 테스트가 진행되었을 시 TEMP_COMPANY 를 MEUMS_COMPANY 로 변경한다.   
  
현재 읽는 속도를 위해 PQ 파일을 다루지만 실제 DB와 PQ의 Sync 를 맞춰주는 작업이 별도로 필요하다.  
  
위 작업은 많은 시간이 소요되기 때문에 후에 수정하는 것이 바람직하다.  
  
login 기능은 flask 서버의 캐시 때문에 한번 입력하면 일정 기간 동안은 재 로그인 할 필요가 없다.  
