# **BI_IMAGE_LABELING_DASHBOARD**
___

## 사용 URL LINK
___
http://192.168.0.83:8050/

category별 상품 이미지를 보여주기 위한 dash site입니다.   

## 사용하는 db
___
image를 얻기 위해 회사내 여러 db를 참조 하였습니다.  
 *read* :

**133.186.134.155** 의 lf-bigdata-real-5 db

 -> **MLF_CATAGORY, MLF_GOODS_CATE, MLF_GOODS** table  
  
**133.186.143.65** 의 wspider db   
 -> **MWS_COLT_ITEM, MWS_COLT_IMAGE** table   

database query flow는 다음과 같습니다.

![Alt text](https://github.com/benepopds/epop_poi/blob/master/intern/BI_image_labeling_dashboard/img/flow.PNG)


## 기능
___
불러온 이미지는 **2000개**로 image_list에 저장한 뒤  
10개의 pagination 된 페이지 마다 **200개씩 display** 됩니다.

예시)
![Alt text](https://github.com/benepopds/epop_poi/blob/master/intern/BI_image_labeling_dashboard/img/dashboard.png)
