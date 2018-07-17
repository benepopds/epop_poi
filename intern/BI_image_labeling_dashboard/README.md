category별 상품 이미지를 보여주기 위한 dash site입니다.  

image를 얻기 위해 회사내 여러 db를 참조 하였습니다.  

**133.186.134.155** 의 lf-bigdata-real-5 db의 **MLF_CATAGORY, MLF_GOODS_CATE, MLF_GOODS** table을 참조 하였고,  
  
**133.186.143.65** 의 wspider db의 **MWS_COLT_ITEM, MWS_COLT_IMAGE** table을 참조 하였습니다.    

database query flow는 다음과 같습니다.

![Alt text](https://github.com/benepopds/epop_poi/blob/master/intern/BI_image_labeling_dashboard/img/flow.PNG)


불러온 이미지는 2000개로 image_list에 저장한 뒤 10개의 pagination 된 각 페이지 마다 200개씩 display 됩니다.

예시)
![Alt text](https://github.com/benepopds/epop_poi/blob/master/intern/BI_image_labeling_dashboard/img/dashboard.png)
