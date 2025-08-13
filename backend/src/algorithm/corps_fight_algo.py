from .base_algo import BaseAlgorithm
import matplotlib.pyplot as plt
from pathlib import Path
# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class CorpsFightAlgorithm(BaseAlgorithm):
    
    def process(
        self, uuid, submit_logs, cur_main_round, cur_sub_round, is_last_round
    ) -> dict[str, str]:
        super().process(uuid, submit_logs, cur_main_round, cur_sub_round, is_last_round)
        if uuid is None:
            return {}
        
        # 图片保存路径
        self.chart_save_path = Path(__file__).parent.parent.parent / "assets" / "lab" / "corps_fight"
        self.chart_save_path.mkdir(parents=True, exist_ok=True)

        # 获取自己的组别和角色
        my_team, my_role = self.experiment_devices[uuid]["role"]
        enemy_team = "B" if my_team == "A" else "A"

        # 获取所有uuid的组别
        uuid_group_map = {
            u: info["role"][0] for u, info in self.experiment_devices.items()
        }

        # 获取小回合总数
        num_sub_rounds = len(self.sub_rounds) if hasattr(self, "sub_rounds") else 3
        
        # 若为最后一轮，调整主回合数
        if is_last_round:
            cur_main_round += 1

        # 查找统帅小回合1选择
        def find_tongshuai_choice(uuid, main_round, sub_round_offset=0):
            target_idx = main_round * num_sub_rounds + sub_round_offset
            if target_idx >= len(submit_logs):
                return ""
            target_round = submit_logs[target_idx]
            return target_round.get(uuid, {}).get("decision", "")

        # 统计战场人数
        def count_battle(round_log, team, battle_name):
            return sum(
                1
                for u, info in round_log.items()
                if uuid_group_map.get(u) == team and info["decision"] == battle_name
            )

        # 计算军团单个大回和得分（含连胜加成）
        def calculate_round_score(main_round, streak_counts):
            last_sub_idx = (main_round + 1) * num_sub_rounds - 1
            if last_sub_idx >= len(submit_logs):
                return {"A": 0, "B": 0}
            round_log = submit_logs[last_sub_idx]
            # 统计统帅的选择
            battle1_A = count_battle(round_log, "A", "战场1")
            battle1_B = count_battle(round_log, "B", "战场1")
            battle2_A = count_battle(round_log, "A", "战场2")
            battle2_B = count_battle(round_log, "B", "战场2")
            # 基础得分计算
            score_A = score_B = 0
            # 战场1计算
            if battle1_A > battle1_B:
                base_score = (battle1_A - battle1_B) * 2 + battle1_A
                score_A += base_score * (streak_counts["A"]["战场1"])
                score_B += 0
            elif battle1_A < battle1_B:
                base_score = (battle1_B - battle1_A) * 2 + battle1_B
                score_B += base_score * (streak_counts["B"]["战场1"])
                score_A += 0
            # 战场2计算
            if battle2_A > battle2_B:
                base_score = (battle2_A - battle2_B) * 2 + battle2_A
                score_A += base_score * (streak_counts["A"]["战场2"])
                score_B += 0
            elif battle2_A < battle2_B:
                base_score = (battle2_B - battle2_A) * 2 + battle2_B
                score_B += base_score * (streak_counts["B"]["战场2"])
                score_A += 0
            return {"A": score_A, "B": score_B}

        # 更新连胜计数
        def update_streak_counts(main_round, current_streak_counts):
            last_sub_idx = (main_round + 1) * num_sub_rounds - 1
            if last_sub_idx >= len(submit_logs):
                return current_streak_counts
            round_log = submit_logs[last_sub_idx]
            # 统计各战场人数
            battle1_A = count_battle(round_log, "A", "战场1")
            battle1_B = count_battle(round_log, "B", "战场1")
            battle2_A = count_battle(round_log, "A", "战场2")
            battle2_B = count_battle(round_log, "B", "战场2")
            new_streak_counts = {
                "A": {
                    "战场1": current_streak_counts["A"]["战场1"],
                    "战场2": current_streak_counts["A"]["战场2"],
                },
                "B": {
                    "战场1": current_streak_counts["B"]["战场1"],
                    "战场2": current_streak_counts["B"]["战场2"],
                },
            }
            # 更新战场1的连胜
            if battle1_A > battle1_B:
                new_streak_counts["A"]["战场1"] += 1
                new_streak_counts["B"]["战场1"] = 0
            elif battle1_A < battle1_B:
                new_streak_counts["B"]["战场1"] += 1
                new_streak_counts["A"]["战场1"] = 0
            else:  # 平局
                new_streak_counts["A"]["战场1"] = 0
                new_streak_counts["B"]["战场1"] = 0
            # 更新战场2的连胜
            if battle2_A > battle2_B:
                new_streak_counts["A"]["战场2"] += 1
                new_streak_counts["B"]["战场2"] = 0
            elif battle2_A < battle2_B:
                new_streak_counts["B"]["战场2"] += 1
                new_streak_counts["A"]["战场2"] = 0
            else:  # 平局
                new_streak_counts["A"]["战场2"] = 0
                new_streak_counts["B"]["战场2"] = 0
            return new_streak_counts

        # 计算总分
        def count_cumulative_scores():
            army_scores = {"A": 0, "B": 0}
            streak_counts = {
                "A": {"战场1": 0, "战场2": 0},
                "B": {"战场1": 0, "战场2": 0},
            }
            for main_round in range(cur_main_round + 1):
                # 更新连胜数
                streak_counts = update_streak_counts(main_round, streak_counts)
                # 计算当前回合的得分（使用当前的连胜数）
                round_score = calculate_round_score(main_round, streak_counts)
                print(f"--- 回合 {main_round+1} ---")
                print(f"当前连胜数: A={streak_counts['A']}, B={streak_counts['B']}")
                print(f"军团回合得分: A={round_score['A']}, B={round_score['B']}")
                army_scores["A"] += round_score["A"]
                army_scores["B"] += round_score["B"]
            return army_scores, streak_counts

        # 计算所有统帅的得分
        def calculate_tongshuai_scores():
            """
            计算所有统帅的得分（支持多个统帅）
            返回:
            - per_round_scores: 每个回合每个统帅的得分 {round: {user_id: score}}
            - cumulative_scores: 每个统帅的累计得分 {user_id: total_score}
            """
            per_round_scores = {}
            cumulative_scores = {}
            for main_round in range(cur_main_round + 1):
                last_sub_idx = (main_round + 1) * num_sub_rounds - 1
                if last_sub_idx >= len(submit_logs):
                    continue
                round_log = submit_logs[last_sub_idx]
                per_round_scores[main_round] = {}
                # 统计各战场人数
                battle1_A = count_battle(round_log, "A", "战场1")
                battle1_B = count_battle(round_log, "B", "战场1")
                battle2_A = count_battle(round_log, "A", "战场2")
                battle2_B = count_battle(round_log, "B", "战场2")
                # 找出所有统帅及其选择
                for user_id, info in round_log.items():
                    role = info.get("role", ("", ""))
                    if role[1] == "统帅":
                        decision = info.get("decision", "")
                        score = 0
                        # 计算该统帅得分
                        if decision == "战场1":
                            if role[0] == "A":
                                if battle1_A > battle1_B:
                                    score = 3
                                elif battle1_A == battle1_B:
                                    score = 1
                            else:  # B队
                                if battle1_B > battle1_A:
                                    score = 3
                                elif battle1_B == battle1_A:
                                    score = 1
                        elif decision == "战场2":
                            if role[0] == "A":
                                if battle2_A > battle2_B:
                                    score = 3
                                elif battle2_A == battle2_B:
                                    score = 1
                            else:  # B队
                                if battle2_B > battle2_A:
                                    score = 3
                                elif battle2_B == battle2_A:
                                    score = 1
                        per_round_scores[main_round][user_id] = score
                        cumulative_scores[user_id] = (
                            cumulative_scores.get(user_id, 0) + score
                        )
            return per_round_scores, cumulative_scores

        # 计算所有参谋的得分
        def calculate_canmou_scores():
            """
            计算所有参谋的得分（支持多个参谋）
            返回:
            - per_round_scores: 每个回合每个参谋的得分 {round: {user_id: score}}
            - cumulative_scores: 每个参谋的累计得分 {user_id: total_score}
            - purchase_records: 购买记录 {round: {team: "购买" or "不购买"}}
            """
            per_round_scores = {}
            cumulative_scores = {}
            purchase_records = {}
            # 先计算每个大回合的军团得分
            round_army_scores = {}
            streak_counts = {
                "A": {"战场1": 0, "战场2": 0},
                "B": {"战场1": 0, "战场2": 0},
            }
            for main_round in range(cur_main_round + 1):
                streak_counts = update_streak_counts(main_round, streak_counts)
                round_score = calculate_round_score(main_round, streak_counts)
                round_army_scores[main_round] = round_score
            for main_round in range(cur_main_round + 1):
                sub_round_idx = main_round * num_sub_rounds + 1
                if sub_round_idx >= len(submit_logs):
                    continue
                round_log = submit_logs[sub_round_idx]
                per_round_scores[main_round] = {}
                purchase_records[main_round] = {"A": "", "B": ""}
                # 先记录各军团是否购买信息
                for user_id, info in round_log.items():
                    role = info.get("role", ("", ""))
                    if role[1] == "参谋":
                        team = role[0]
                        purchas_state = info.get("decision", "")
                        purchase_records[main_round][team] = purchas_state
                # 计算每个参谋得分
                for user_id, info in round_log.items():
                    role = info.get("role", ("", ""))
                    if role[1] == "参谋":
                        team = role[0]
                        purchased = purchase_records[main_round][team] == "购买"
                        # 得分 = 军团该回合得分 - 购买成本
                        army_score = round_army_scores[main_round][team]
                        cost = 1 if purchased else 0
                        score = army_score - cost
                        per_round_scores[main_round][user_id] = score
                        cumulative_scores[user_id] = (
                            cumulative_scores.get(user_id, 0) + score
                        )
            return per_round_scores, cumulative_scores, purchase_records

        # 队伍得分图表生成函数
        def generate_team_score_chart():
            """生成队伍得分折线图"""
            
            try:
                # 创建图片文件名
                # 生成实验唯一标识，用于队伍相关图片命名
                if not hasattr(self, '_experiment_id'):
                    # 基于参与实验的所有UUID生成唯一标识
                    all_uuids = sorted(self.experiment_devices.keys())
                    combined = ''.join(all_uuids)
                    import hashlib
                    self._experiment_id = hashlib.md5(combined.encode()).hexdigest()[:8]
                filename = f"score_chart_{my_team}_{cur_main_round}_{self._experiment_id}.png"
                filepath = self.chart_save_path / filename
                
                # 检查文件是否已存在，如果存在则直接返回文件名
                if filepath.exists():
                    print(f"队伍得分图表已存在，跳过生成: {filename}")
                    return filename
                
                # 计算每轮得分历史
                rounds = list(range(cur_main_round + 1))
                my_scores = []
                enemy_scores = []
                
                # 重新计算每轮累计得分
                streak_counts = {
                    "A": {"战场1": 0, "战场2": 0},
                    "B": {"战场1": 0, "战场2": 0},
                }
                cumulative_A = 0
                cumulative_B = 0
                
                for round_num in rounds:
                    if round_num == 0:
                        # 第0轮初始状态，得分为0
                        my_scores.append(0)
                        enemy_scores.append(0)
                    else:  # 计算已完成的轮次得分
                        # 更新连胜数
                        streak_counts = update_streak_counts(round_num - 1, streak_counts)
                        # 计算当前回合得分
                        round_score = calculate_round_score(round_num - 1, streak_counts)
                        cumulative_A += round_score["A"]
                        cumulative_B += round_score["B"]
                        
                        if my_team == "A":
                            my_scores.append(cumulative_A)
                            enemy_scores.append(cumulative_B)
                        else:
                            my_scores.append(cumulative_B)
                            enemy_scores.append(cumulative_A)
                # 创建图表
                plt.figure(figsize=(10, 6))
                if is_last_round:
                    print(rounds)
                    print(my_scores)
                plt.plot(rounds, my_scores, marker='o', linewidth=2, label=f'我军({my_team}队)', color='blue')
                plt.plot(rounds, enemy_scores, marker='s', linewidth=2, label=f'敌军({enemy_team}队)', color='red')
                
                plt.title('军团累计得分对比', fontsize=25, fontweight='bold')
                plt.xlabel('回合数', fontsize=20)
                plt.ylabel('累计得分', fontsize=20)
                plt.tick_params(axis='both', which='major', labelsize=16)
                plt.legend(fontsize=20)
                plt.grid(True, alpha=0.3)
                plt.tight_layout()
                
                # 保存图片
                plt.savefig(filepath, dpi=300, bbox_inches='tight')
                plt.close()
                
                return filename
                
            except Exception as e:
                print(f"生成图表失败: {e}")
                return "3.png"  # 返回默认图片

        # 个人得分图表生成函数
        def generate_personal_score_chart(score_history):
            """生成个人得分折线图"""
            try:
                filename = f"personal_chart_{my_role}_{cur_main_round}_{uuid}.png"
                filepath = self.chart_save_path / filename
                # 检查文件是否已存在，如果存在则直接返回文件名
                if filepath.exists():
                    print(f"个人得分图表已存在，跳过生成: {filename}")
                    return filename
                
                rounds = list(range(cur_main_round + 1))
                personal_scores = []
                
                cumulative_score = 0
                for round_num in rounds:
                    if round_num == 0:
                        # 第0轮初始状态，得分为0
                        personal_scores.append(0)
                    else:
                        round_score = score_history.get(round_num-1, {}).get(uuid, 0)
                        cumulative_score += round_score
                        personal_scores.append(cumulative_score)
                
                plt.figure(figsize=(10, 6))
                color = 'green' if my_role == "统帅" else 'orange'
                plt.plot(rounds, personal_scores, marker='o', linewidth=2, label=f'本{my_role}得分', color=color)
                
                plt.title(f'{my_role}累计得分趋势', fontsize=25, fontweight='bold')
                plt.xlabel('回合数', fontsize=20)
                plt.ylabel('累计得分', fontsize=20)
                plt.tick_params(axis='both', which='major', labelsize=16)
                plt.legend(fontsize=20)
                plt.grid(True, alpha=0.3)
                plt.tight_layout()
                
                # 保存图片
                plt.savefig(filepath, dpi=300, bbox_inches='tight')
                plt.close()
                
                return filename
                
            except Exception as e:
                print(f"生成个人图表失败: {e}")
                return "4.png"  # 返回默认图片

        # 计算各类得分
        cumulative_scores, streak_counts = count_cumulative_scores()
        tongshuai_per_round, tongshuai_cumulative = calculate_tongshuai_scores()
        canmou_per_round, canmou_cumulative, purchase_records = (
            calculate_canmou_scores()
        )
        
        # 生成各类图表
        score_chart_filename = generate_team_score_chart()
        print(f"生成队伍得分图表: {score_chart_filename}")
        if my_role == "统帅":
            personal_chart_filename = generate_personal_score_chart(tongshuai_per_round)
        else:  # 参谋
            personal_chart_filename = generate_personal_score_chart(canmou_per_round)
        print(f"生成个人得分图表: {personal_chart_filename}")
        
        # 生成return结果
        result = {"infos": [], "images": []}
        # 小回合1（统帅决策）
        if is_last_round == False:
            if cur_sub_round == 0 and my_role == "统帅":
                # 历史信息
                history_infos = [("#info_group", "历史信息")]
                if cur_main_round > 0:
                    idx3 = cur_main_round * num_sub_rounds - 1
                    round3 = submit_logs[idx3] if idx3 < len(submit_logs) else {}
                    current_score = calculate_round_score(cur_main_round - 1, streak_counts)
                    history_infos.extend([
                        ("前一个大回合我军得分#[解释： 前一个回合我军得分bala]", str(current_score[my_team])),
                        ("前一个大回合本统帅得分#[解释： 前一个回合本统帅得分bala]", str(tongshuai_per_round.get(cur_main_round - 1, {}).get(uuid, 0))),
                        ("前一个大回合我军战场1人数#[解释： 前一个回合我军战场1人数bala]", str(count_battle(round3, my_team, "战场1"))),
                        ("前一个大回合我军战场2人数#[解释： 前一个回合我军战场2人数bala]", str(count_battle(round3, my_team, "战场2"))),
                        ("前一个大回合敌军战场1人数#[解释： 前一个回合敌军战场1人数bala]", str(count_battle(round3, enemy_team, "战场1"))),
                        ("前一个大回合敌军战场2人数#[解释： 前一个回合敌军战场2人数bala]", str(count_battle(round3, enemy_team, "战场2"))),
                        ("前一个大回合本统帅最终选择#[解释： 前一个回合本统帅最终选择bala]", find_tongshuai_choice(uuid, cur_main_round - 1, 2)),
                    ])
                else:
                    history_infos.extend([
                        ("前一个大回合我军得分#[解释： 前一个回合我军得分bala]", "0"),
                        ("前一个大回合本统帅得分#[解释： 前一个回合本统帅得分bala]", "0"),
                    ])

                # 统计信息
                statistics_infos = [
                    ("#info_group", "统计信息"),
                    ("我军累计得分#[解释： 我军累计得分bala]", str(cumulative_scores[my_team]) if cur_main_round > 0 else "0"),
                    ("本统帅累计得分#[解释： 本统帅累计得分bala]", str(tongshuai_cumulative.get(uuid, 0)) if cur_main_round > 0 else "0"),
                    ("当前我军战场1连胜数#[解释： 当前我军战场1连胜数bala]", str(streak_counts[my_team]["战场1"])),
                    ("当前我军战场2连胜数#[解释： 当前我军战场2连胜数bala]", str(streak_counts[my_team]["战场2"])),
                ]

                result["infos"] = history_infos + statistics_infos
                result["images"] = [score_chart_filename, personal_chart_filename]


            # 小回合2（参谋决策）
            elif cur_sub_round == 1 and my_role == "参谋":

                idx1 = cur_main_round * num_sub_rounds
                round1 = submit_logs[idx1] if idx1 < len(submit_logs) else {}

                # 历史信息部分
                history_infos = [("#info_group", "历史信息")]
                
                if cur_main_round > 0:
                    idx2 = (cur_main_round - 1) * num_sub_rounds + 1
                    advisor_decision = submit_logs[idx2].get(uuid, {}).get("decision", "")
                    last_score = calculate_round_score(cur_main_round - 1, streak_counts)
                    history_infos.extend([
                        ("前一个大回合我军得分#[解释： 前一个回合我军的得分bala]", str(last_score[my_team])),
                        ("前一个大回合本参谋得分#[解释： 前一个回合本参谋得分bala]", str(canmou_per_round.get(cur_main_round - 1, {}).get(uuid, 0))),
                        ("前一个大回合本参谋选择#[解释： 前一个回合本参谋选择bala]", advisor_decision),
                    ])
                else:
                    history_infos.extend([
                        ("前一个大回合我军得分#[解释： 前一个回合我军的得分bala]", "0"),
                        ("前一个大回合本参谋得分#[解释： 前一个回合本参谋得分bala]", "0"),
                    ])
                
                # 统计信息部分
                statistics_infos = [
                    ("#info_group", "统计信息"),
                    ("我军累计得分#[解释： 我军累计得分bala]", str(cumulative_scores[my_team]) if cur_main_round > 0 else "0"),
                    ("本参谋累计得分#[解释： 本参谋累计得分bala]", str(canmou_cumulative.get(uuid, 0)) if cur_main_round > 0 else "0"),
                    ("本大回合中小回合1我军战场1人数#[解释： 本大回合中小回合1我军战场1人数bala]", str(count_battle(round1, my_team, "战场1"))),
                    ("本大回合中小回合1我军战场2人数#[解释： 本大回合中小回合1我军战场2人数bala]", str(count_battle(round1, my_team, "战场2"))),
                    ("当前我军战场1连胜数#[解释： 当前我军战场1连胜数bala]", str(streak_counts[my_team]["战场1"])),
                    ("当前我军战场2连胜数#[解释： 当前我军战场2连胜数bala]", str(streak_counts[my_team]["战场2"])),
                ]
                
                # 合并历史信息和统计信息
                result["infos"] = history_infos + statistics_infos
                result["images"] = [score_chart_filename, personal_chart_filename]

            # 小回合3（统帅决策）
            elif cur_sub_round == 2 and my_role == "统帅":
                idx1 = cur_main_round * num_sub_rounds
                round1 = submit_logs[idx1] if idx1 < len(submit_logs) else {}
                buy = purchase_records.get(cur_main_round, {}).get(my_team, "")

                # 历史信息
                history_infos = [("#info_group", "历史信息")]
                if cur_main_round > 0:
                    last_round_score = calculate_round_score(cur_main_round - 1, streak_counts)
                    history_infos.extend([
                        ("前一个大回合我军得分#[解释： 前一个回合我军的得分bala]", str(last_round_score[my_team])),
                        ("前一个大回合本统帅得分#[解释： 前一个回合本参谋得分bala]", str(tongshuai_per_round.get(cur_main_round - 1, {}).get(uuid, 0))),
                    ])
                else:
                    history_infos.extend([
                        ("前一个大回合我军得分#[解释： 前一个回合我军的得分bala]", "0"),
                        ("前一个大回合本统帅得分#[解释： 前一个回合本参谋得分bala]", "0"),
                    ])

                # 统计信息
                statistics_infos = [
                    ("#info_group", "统计信息"),
                    ("我军累计得分#[解释： 我军累计得分bala]", str(cumulative_scores[my_team])),
                    ("本统帅累计得分#[解释： 本统帅累计得分bala]", str(tongshuai_cumulative.get(uuid, 0))),
                    ("本大回合中小回合1本统帅选择#[解释： 本大回合中小回合1本统帅选择bala]", find_tongshuai_choice(uuid, cur_main_round, 0)),
                    ("本大回合中小回合1我军战场1人数#[解释： 本大回合中小回合1我军战场1人数bala]", str(count_battle(round1, my_team, "战场1"))),
                    ("本大回合中小回合1我军战场2人数#[解释： 本大回合中小回合1我军战场2人数bala]", str(count_battle(round1, my_team, "战场2"))),
                    ("当前我军战场1连胜数#[解释： 当前我军战场1连胜数bala]", str(streak_counts[my_team]["战场1"])),
                    ("当前我军战场2连胜数#[解释： 当前我军战场2连胜数bala]", str(streak_counts[my_team]["战场2"])),
                ]

                # 根据是否购买信息添加敌军信息
                if buy == "购买":
                    statistics_infos.extend([
                        ("本大回合中小回合1敌军战场1人数#[解释： 本大回合中小回合1敌军战场1人数bala]", str(count_battle(round1, enemy_team, "战场1"))),
                        ("本大回合中小回合1敌军战场2人数#[解释： 本大回合中小回合1敌军战场2人数bala]", str(count_battle(round1, enemy_team, "战场2"))),
                    ])
                elif buy == "不购买":
                    statistics_infos.extend([
                        ("本大回合中小回合1敌军战场1人数#[解释： 本大回合中小回合1敌军战场1人数bala]", "未购买"),
                        ("本大回合中小回合1敌军战场2人数#[解释： 本大回合中小回合1敌军战场2人数bala]", "未购买"),
                    ])

                result["infos"] = history_infos + statistics_infos
                result["images"] = [score_chart_filename, personal_chart_filename]
                
            print(
                f"本轮主回合:{cur_main_round},\n本轮小回合: {cur_sub_round}, \n本轮轮策者: {my_role}, \n当前队伍: {my_team}, \n信息界面：{result}\n"
            )
            # print(f"实验日志：{submit_logs}")
        else:
            # 最后一轮，输出最终结果
            if my_role == "统帅":
                cur_sub_round = 0
                idx3 = cur_main_round * num_sub_rounds - 1
                round3 = submit_logs[idx3] if idx3 < len(submit_logs) else {}
                current_score = calculate_round_score(cur_main_round - 1, streak_counts)
                
                result["infos"] = [
                        ("#info_group", "历史信息"),
                        ("前一个大回合我军得分", str(current_score[my_team])),
                        ("前一个大回合本统帅得分", str(tongshuai_per_round.get(cur_main_round - 1, {}).get(uuid, 0))),
                        ("前一个大回合我军战场1人数", str(count_battle(round3, my_team, "战场1"))),
                        ("前一个大回合我军战场2人数", str(count_battle(round3, my_team, "战场2"))),
                        ("前一个大回合敌军战场1人数", str(count_battle(round3, enemy_team, "战场1"))),
                        ("前一个大回合敌军战场2人数", str(count_battle(round3, enemy_team, "战场2"))),
                        ("前一个大回合本统帅最终选择", find_tongshuai_choice(uuid, cur_main_round - 1, 2)),
                        ("#info_group", "统计信息"),
                        ("我军累计得分", str(cumulative_scores[my_team])),
                        ("本统帅累计得分", str(tongshuai_cumulative.get(uuid, 0))),
                        ("当前我军战场1连胜数", str(streak_counts[my_team]["战场1"])),
                        ("当前我军战场2连胜数", str(streak_counts[my_team]["战场2"])),
                                    ]
            
            elif my_role == "参谋":
                cur_sub_round = 1
                idx1 = cur_main_round * num_sub_rounds
                round1 = submit_logs[idx1] if idx1 < len(submit_logs) else {}
                idx2 = (cur_main_round - 1) * num_sub_rounds + 1
                advisor_decision = (submit_logs[idx2].get(uuid, {}).get("decision", ""))  # 前一个大回和参谋决策
                last_score = calculate_round_score(cur_main_round - 1, streak_counts)
                
                result["infos"] = [
                        ("#info_group", "历史信息"),
                        ("前一个大回合我军得分", str(last_score[my_team])),
                        ("前一个大回合本参谋得分", str(canmou_per_round.get(cur_main_round - 1, {}).get(uuid, 0))),
                        ("前一个大回合本参谋选择", advisor_decision),
                        ("#info_group", "统计信息"),
                        ("我军累计得分", str(cumulative_scores[my_team])),
                        ("本参谋累计得分", str(canmou_cumulative.get(uuid, 0))),
                        ("当前我军战场1连胜数", str(streak_counts[my_team]["战场1"])),
                        ("当前我军战场2连胜数", str(streak_counts[my_team]["战场2"])),
                                    ]
            
            # 最后一轮也显示图表
            result["images"] = [score_chart_filename, personal_chart_filename]
            print(
                f"用户ID: {uuid}, \n角色: {my_role}, \n队伍: {my_team}, \n得分情况：{result}\n"
            )
        return result
