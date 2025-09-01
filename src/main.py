from enum import Enum
import json
import datetime

# 할인율
class Discount(Enum):
    BASIC = 0    # 일반 차량
    LPG = 30     # LPG 차량
    ELEC = 50    # 전기 차량

# 요금표
class Charge(Enum):
    hour = 6000
    min = 1000
    free = 0     # 30분 미만

# 정기차량 목록 (dict)
mon_parking = {
    "0627": {
        "startTime": "08:28:01:10",
        "parkingArea": "2F 10",
        "Discount": Discount.LPG.value,
    },
    "0001": {
        "startTime": "08:28:01:10",
        "parkingArea": "1F 7",
        "Discount": Discount.BASIC.value,
    },
}

# 일반차량 목록 (dict)
parking = {
    "0000": {
        "startTime": "08:28:01:10",
        "parkingArea": "3F 1",
        "Discount": Discount.ELEC.value,
    }
}

# 주차타워 (5 * 10) 생성
parkinglot = [['□'] * 10 for _ in range(5)]
# 기존 등록된 정기차량/일반차량 주차위치 반영
for rec in list(parking.values()) + list(mon_parking.values()):
    try:
        fl, sl = map(int, rec["parkingArea"].split("F "))
        parkinglot[fl - 1][sl - 1] = "■"
    except Exception:
        # parkingArea 형식이 잘못된 경우 무시
        pass

# 현재 상태 출력
print("\n===== 현재 주차 현황 =====")
for i in range(5):
    print(f'{i+1}층 {parkinglot[i]}')
print("일반차량 목록:", json.dumps(parking, indent=4, ensure_ascii=False))
print("정기차량 목록:", json.dumps(mon_parking, indent=4, ensure_ascii=False))
print("==========================")

#---------- 메인 ----------#
while True:
    menu = input("메뉴를 선택하세요 (입차=1, 출차=2, 종료=0): ").strip()

    if menu == "0":
        print("프로그램을 종료합니다.")
        break

    # ---------- 입차 ---------- #
    elif menu == "1":
        #- 사용자 입력 -#
        carNum = input("차량 번호 4자리를 입력해주세요: ")
        startTime = input("입차 시간을 입력해주세요(MM:DD:hh:mm): ")
        
        # 입력된 주차 위치가 중복되는지 검증
        while True:
            parkingArea = input("주차 위치를 입력해주세요(0F 0): ")
            fl, sl = map(int, parkingArea.split("F "))

            if parkinglot[fl - 1][sl - 1] == "■":
                print("이미 주차된 자리입니다. 다른 자리를 입력해주세요.")
                continue
            else:
                break

        # 정기차량이면: 일반차량 목록에 넣지 않고, 입차시간만 업데이트
        if carNum in mon_parking:
            # - 사용자 데이터 업데이트 -#
            mon_parking[carNum]["startTime"] = startTime
            mon_parking[carNum]["parkingArea"] = parkingArea
            # - 입차 처리 -# (정기차량은 고정 자리 사용)
            fl, sl = map(int, mon_parking[carNum]["parkingArea"].split("F "))
            parkinglot[fl - 1][sl - 1] = "■"  # 정기 지정 자리로 입차 업데이트

            # - 입차 업데이트 후 출력 -#
            print("주차가 완료되었습니다. (정기차량: 입차시간만 업데이트)")
            for i in range(5):
                print(f'{i+1}층 {parkinglot[i]}')
        else:
            #- 사용자 데이터 추가 -#
            parking[carNum] = {
                "startTime": startTime,
                "parkingArea": parkingArea,
                "Discount": Discount.BASIC.value,
            }

            #- 입차 처리 -#
            parkingArea_list = list(map(int, parkingArea.split("F ")))  # 숫자만 리스트에 저장
            parkinglot[parkingArea_list[0] - 1][parkingArea_list[1] - 1] = "■"  # 입차 업데이트

            #- 입차 업데이트 후 출력 -#
            print("주차가 완료되었습니다.")
            for i in range(5):
                print(f'{i+1}층 {parkinglot[i]}')

    #---------- 출차 ----------#
    elif menu == "2":
        # 사용자 입력
        carNum = input("차량 번호 4자리를 입력해주세요: ")
        rec = parking.get(carNum) or mon_parking.get(carNum)
        if not rec:
            print("해당 차량 정보가 없습니다.")
            continue

        print(json.dumps(rec, indent=4))
        endTime = input("출차 시간을 입력해주세요(MM:DD:hh:mm): ")

        #- 요금 계산 -#
        # 차량에 저장된 입차시간/할인율로 계산
        # 정기/일반 공통으로 이미 가져온 rec 사용
        start_str = rec["startTime"]
        # 정기차량이면 mon_parking의 Discount 사용, 아니면 parking의 Discount 사용 (없으면 basic값)
        disc_pct = int(rec.get("Discount", Discount.BASIC.value))

        # 문자를 숫자로 변환 (입차 시간)
        sm, sd, sh, smin = map(int, start_str.split(":"))
        start_dt = datetime.datetime(2000, sm, sd, sh, smin)

        # 출차 시간에 올바른 값이 들어올 때까지 반복
        while True:
            try:
                em, ed, eh, emin = map(int, endTime.split(":"))
                end_dt = datetime.datetime(2000, em, ed, eh, emin)

                minutes_exact = (end_dt - start_dt).total_seconds() / 60
                if minutes_exact < 0:
                    print("출차 시간이 입차 시간보다 빠릅니다.")
                    endTime = input("출차 시간을 입력해주세요(MM:DD:hh:mm): ")
                else:
                    break
            except ValueError:
                print("형식이 잘못되었습니다. 예) 03:22:12:13")
                endTime = input("출차 시간을 입력해주세요(MM:DD:hh:mm): ")

        # 10분 단위 내림
        total_minutes = (int(minutes_exact) // 10) * 10

        # 30분 무료
        FREE_MINUTES = 30
        if total_minutes <= FREE_MINUTES:
            base_fee = 0
        else:
            billable = total_minutes - FREE_MINUTES
            units_10min = billable // 10
            base_fee = units_10min * Charge.min.value  # 10분당 요금

        # 할인 적용
        final_fee = int(base_fee * (100 - disc_pct) / 100)

        # 요금출력
        print(f'{carNum} 차량의 요금은 {final_fee} 입니다.')
        aws = input("출차를 하시겠습니까?(y/n): ")
        if aws == "y":
            print("정산이 완료되었습니다.")
            # 자리 비우기
            rec = parking.get(carNum) or mon_parking.get(carNum)
            if rec:
                fl, sl = map(int, rec["parkingArea"].split("F "))
                parkinglot[fl - 1][sl - 1] = "□"
            # 일반차량이면 목록에서 제거 (정기차량은 유지)
            if carNum not in mon_parking and carNum in parking:
                del parking[carNum]
            # 상태 출력
            print("출차가 완료되었습니다. 현재 주차 현황:")
            for i in range(5):
                print(f'{i+1}층 {parkinglot[i]}')
        else:
            print("출차를 취소했습니다.")