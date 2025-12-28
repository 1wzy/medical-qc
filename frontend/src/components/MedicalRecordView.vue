<template>
  <div class="medical-record-view">
    <!-- 页面导航 -->
    <div class="page-navigation-top">
      <el-tabs v-model="currentPage" type="card" @tab-change="handleTabChange">
        <el-tab-pane label="基本信息" name="basic">
          <template #label>
            <span>基本信息</span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="诊断信息" name="diagnosis">
          <template #label>
            <span>诊断信息</span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="手术信息" name="surgery">
          <template #label>
            <span>手术信息</span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="入院记录" name="admission">
          <template #label>
            <span>入院记录</span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="出院记录" name="discharge">
          <template #label>
            <span>出院记录</span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="手术记录" name="operation">
          <template #label>
            <span>手术记录</span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="病程记录" name="course">
          <template #label>
            <span>病程记录 ({{ getCourseRecords().length }})</span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="医嘱记录" name="orders">
          <template #label>
            <span>医嘱记录 ({{ getOrders().length }})</span>
          </template>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- 基本信息页面 -->
    <div class="record-page" v-if="currentPage === 'basic'">
      <div class="page-header">
        <h2>基本信息</h2>
      </div>

      <!-- 从病案首页获取基本信息 -->
      <div class="section" v-if="getHomePageData() && Object.keys(getHomePageData()).length > 0">
        <div class="section-title">患者基本信息</div>
        <el-descriptions :column="3" border size="small">
          <el-descriptions-item label="患者ID">
            {{ getHomePageData()['患者ID'] || getHomePageData()['patient_id'] || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="性别">
            {{ getHomePageData()['性别'] || getHomePageData()['gender'] || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="年龄">
            {{ getHomePageData()['年龄'] || getHomePageData()['age'] || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="出生日期">
            {{ getHomePageData()['出生日期'] || getHomePageData()['birth_date'] || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="国籍">
            {{ getHomePageData()['国籍'] || getHomePageData()['nationality'] || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="医疗机构">
            {{ getHomePageData()['医疗机构名称'] || getHomePageData()['hospital_name'] || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="入院时间">
            {{ getHomePageData()['入院时间'] || getHomePageData()['admission_time'] || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="出院时间">
            {{ getHomePageData()['出院时间'] || getHomePageData()['discharge_time'] || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="实际住院天数">
            {{ getHomePageData()['实际住院天数'] || getHomePageData()['actual_days'] || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="入院途径">
            {{ getHomePageData()['入院途径'] || getHomePageData()['admission_way'] || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="入院科别">
            {{ getHomePageData()['入院科别'] || getHomePageData()['admission_dept'] || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="入院病房">
            {{ getHomePageData()['入院病房'] || getHomePageData()['admission_ward'] || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="出院科别">
            {{ getHomePageData()['出院科别'] || getHomePageData()['discharge_dept'] || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="出院病房">
            {{ getHomePageData()['出院病房'] || getHomePageData()['discharge_ward'] || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="离院方式">
            {{ getHomePageData()['离院方式'] || getHomePageData()['discharge_way'] || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="有无药物过敏">
            {{ getHomePageData()['有无药物过敏'] || getHomePageData()['drug_allergy'] || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="过敏药物名称" :span="2">
            {{ getHomePageData()['过敏药物名称'] || getHomePageData()['allergy_drug_name'] || '-' }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <el-empty v-else description="暂无基本信息" />
    </div>

    <!-- 诊断信息页面 -->
    <div class="record-page" v-if="currentPage === 'diagnosis'">
      <div class="page-header">
        <h2>诊断信息</h2>
      </div>

      <!-- 主要诊断 -->
      <div class="section" v-if="getHomePageData() && Object.keys(getHomePageData()).length > 0">
        <div class="section-title">主要诊断</div>
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="诊断编码">
            {{ getHomePageData()['出院主要诊断编码'] || getHomePageData()['main_diagnosis_code'] || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="诊断名称">
            {{ getHomePageData()['出院主要诊断名称'] || getHomePageData()['main_diagnosis_name'] || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="入院诊断编码">
            {{ getHomePageData()['入院诊断编码'] || getHomePageData()['admission_diagnosis_code'] || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="入院诊断名称">
            {{ getHomePageData()['入院诊断名称'] || getHomePageData()['admission_diagnosis_name'] || '-' }}
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 其他诊断 -->
      <div class="section" v-if="getOtherDiagnosesList().length > 0">
        <div class="section-title">其他诊断</div>
        <el-table :data="getOtherDiagnosesList()" border size="small">
          <el-table-column type="index" label="#" width="60" align="center" />
          <el-table-column prop="出院其他诊断编码" label="诊断编码" width="150">
            <template #default="{ row }">
              {{ row['出院其他诊断编码'] || row['diagnosis_code'] || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="出院其他诊断名称" label="诊断名称" min-width="200">
            <template #default="{ row }">
              {{ row['出院其他诊断名称'] || row['diagnosis_name'] || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="出院其他诊断入院病情" label="入院病情" width="120" align="center">
            <template #default="{ row }">
              {{ formatAdmissionCondition(row['出院其他诊断入院病情'] || row['admission_condition']) }}
            </template>
          </el-table-column>
          <el-table-column prop="其他诊断出院情况" label="出院情况" min-width="150">
            <template #default="{ row }">
              {{ row['其他诊断出院情况'] || row['discharge_condition'] || '-' }}
            </template>
          </el-table-column>
        </el-table>
      </div>
      <el-empty v-else-if="!getHomePageData() || Object.keys(getHomePageData()).length === 0" description="暂无诊断信息" />
    </div>

    <!-- 手术信息页面 -->
    <div class="record-page" v-if="currentPage === 'surgery'">
      <div class="page-header">
        <h2>手术信息</h2>
      </div>

      <!-- 主要手术 -->
      <div class="section" v-if="getHomePageData() && Object.keys(getHomePageData()).length > 0 && (getHomePageData()['主要手术操作名称'] || getHomePageData()['main_surgery_name'])">
        <div class="section-title">主要手术</div>
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="手术编码">
            {{ getHomePageData()['主要手术操作编码'] || getHomePageData()['main_surgery_code'] || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="手术名称">
            {{ getHomePageData()['主要手术操作名称'] || getHomePageData()['main_surgery_name'] || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="手术日期">
            {{ getHomePageData()['主要手术操作日期'] || getHomePageData()['main_surgery_date'] || '-' }}
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 其他手术操作 -->
      <div class="section" v-if="getOtherSurgeries().length > 0">
        <div class="section-title">其他手术操作</div>
        <el-table :data="getOtherSurgeries()" border size="small">
          <el-table-column type="index" label="#" width="60" align="center" />
          <el-table-column prop="其他手术操作编码" label="手术编码" width="150">
            <template #default="{ row }">
              {{ row['其他手术操作编码'] || row['surgery_code'] || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="其他手术操作名称" label="手术名称" min-width="250">
            <template #default="{ row }">
              {{ row['其他手术操作名称'] || row['surgery_name'] || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="其他手术操作日期" label="手术日期" width="150" align="center">
            <template #default="{ row }">
              {{ row['其他手术操作日期'] || row['surgery_date'] || '-' }}
            </template>
          </el-table-column>
        </el-table>
      </div>
      <el-empty v-else description="暂无手术信息" />
    </div>

    <!-- 入院记录页面 -->
    <div class="record-page" v-if="currentPage === 'admission'">
      <div class="page-header">
        <h2>入院记录</h2>
      </div>

      <div class="section" v-if="getAdmissionRecord() && Object.keys(getAdmissionRecord()).length > 0">
        <div class="section-title">主诉</div>
        <div class="text-content">
          {{ getAdmissionRecord()['主诉'] || getAdmissionRecord()['chief_complaint'] || '-' }}
        </div>
      </div>

      <div class="section" v-if="getAdmissionRecord() && (getAdmissionRecord()['现病史'] || getAdmissionRecord()['present_illness'])">
        <div class="section-title">现病史</div>
        <div class="text-content">
          {{ formatCourseContent(getAdmissionRecord()['现病史'] || getAdmissionRecord()['present_illness'] || '') }}
        </div>
      </div>

      <div class="section" v-if="getAdmissionRecord() && (getAdmissionRecord()['既往史'] || getAdmissionRecord()['past_history'])">
        <div class="section-title">既往史</div>
        <div class="text-content">
          {{ formatCourseContent(getAdmissionRecord()['既往史'] || getAdmissionRecord()['past_history'] || '') }}
        </div>
      </div>

      <div class="section" v-if="getAdmissionRecord() && (getAdmissionRecord()['个人史'] || getAdmissionRecord()['personal_history'])">
        <div class="section-title">个人史</div>
        <div class="text-content">
          {{ formatCourseContent(getAdmissionRecord()['个人史'] || getAdmissionRecord()['personal_history'] || '') }}
        </div>
      </div>

      <div class="section" v-if="getAdmissionRecord() && (getAdmissionRecord()['婚育史'] || getAdmissionRecord()['marriage_history'])">
        <div class="section-title">婚育史</div>
        <div class="text-content">
          {{ formatCourseContent(getAdmissionRecord()['婚育史'] || getAdmissionRecord()['marriage_history'] || '') }}
        </div>
      </div>

      <div class="section" v-if="getAdmissionRecord() && (getAdmissionRecord()['家族史'] || getAdmissionRecord()['family_history'])">
        <div class="section-title">家族史</div>
        <div class="text-content">
          {{ formatCourseContent(getAdmissionRecord()['家族史'] || getAdmissionRecord()['family_history'] || '') }}
        </div>
      </div>

      <div class="section" v-if="getAdmissionRecord() && (getAdmissionRecord()['体格检查'] || getAdmissionRecord()['physical_exam'])">
        <div class="section-title">体格检查</div>
        <div class="text-content">
          {{ formatCourseContent(getAdmissionRecord()['体格检查'] || getAdmissionRecord()['physical_exam'] || '') }}
        </div>
      </div>

      <div class="section" v-if="getAdmissionRecord() && (getAdmissionRecord()['专科情况'] || getAdmissionRecord()['specialty_exam'])">
        <div class="section-title">专科情况</div>
        <div class="text-content">
          {{ formatCourseContent(getAdmissionRecord()['专科情况'] || getAdmissionRecord()['specialty_exam'] || '') }}
        </div>
      </div>

      <div class="section" v-if="getAdmissionRecord() && (getAdmissionRecord()['辅助检查'] || getAdmissionRecord()['auxiliary_exam'])">
        <div class="section-title">辅助检查</div>
        <div class="text-content">
          {{ formatCourseContent(getAdmissionRecord()['辅助检查'] || getAdmissionRecord()['auxiliary_exam'] || '') }}
        </div>
      </div>

      <div class="section" v-if="getAdmissionRecord()">
        <div class="section-title">初步诊断</div>
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="初步诊断">
            {{ getAdmissionRecord()['初步诊断'] || getAdmissionRecord()['preliminary_diagnosis'] || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="入院主要诊断编码">
            {{ getAdmissionRecord()['入院主要诊断编码'] || getAdmissionRecord()['admission_main_diagnosis_code'] || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="入院主要诊断名称" :span="2">
            {{ getAdmissionRecord()['入院主要诊断名称'] || getAdmissionRecord()['admission_main_diagnosis_name'] || '-' }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <el-empty v-else description="暂无入院记录" />
    </div>

    <!-- 出院记录页面 -->
    <div class="record-page" v-if="currentPage === 'discharge'">
      <div class="page-header">
        <h2>出院记录</h2>
      </div>

      <div class="section" v-if="getDischargeRecord() && Object.keys(getDischargeRecord()).length > 0">
        <div class="section-title">出院记录内容</div>
        <div class="text-content">
          {{ formatCourseContent(getDischargeRecord()['文档内容'] || getDischargeRecord()['document_content'] || getDischargeRecord()['content'] || '') }}
        </div>
      </div>

      <div class="section" v-if="getDischargeRecord()">
        <div class="section-title">出院信息</div>
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="入院日期">
            {{ getDischargeRecord()['入院日期'] || getDischargeRecord()['admission_date'] || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="出院日期">
            {{ getDischargeRecord()['出院日期'] || getDischargeRecord()['discharge_date'] || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="入院诊断" :span="2">
            {{ getDischargeRecord()['入院诊断'] || getDischargeRecord()['admission_diagnosis'] || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="出院主要诊断编码">
            {{ getDischargeRecord()['出院主要诊断编码'] || getDischargeRecord()['discharge_main_diagnosis_code'] || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="出院主要诊断名称">
            {{ getDischargeRecord()['出院主要诊断名称'] || getDischargeRecord()['discharge_main_diagnosis_name'] || '-' }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <el-empty v-else description="暂无出院记录" />
    </div>

    <!-- 手术记录页面 -->
    <div class="record-page" v-if="currentPage === 'operation'">
      <div class="page-header">
        <h2>手术记录</h2>
      </div>

      <div class="section" v-if="getOperationRecord() && Object.keys(getOperationRecord()).length > 0">
        <div class="section-title">手术基本信息</div>
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="手术日期">
            {{ getOperationRecord()['手术日期'] || getOperationRecord()['operation_date'] || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="手术编码">
            {{ getOperationRecord()['手术编码'] || getOperationRecord()['operation_code'] || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="手术名称" :span="2">
            {{ getOperationRecord()['手术名称'] || getOperationRecord()['operation_name'] || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="手术级别">
            {{ getOperationRecord()['手术级别'] || getOperationRecord()['operation_level'] || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="麻醉方式">
            {{ getOperationRecord()['麻醉方式'] || getOperationRecord()['anesthesia_method'] || getOperationRecord()['麻醉方法'] || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="手术者">
            {{ getOperationRecord()['手术者及助手姓名'] || getOperationRecord()['surgeon'] || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="手术部位">
            {{ getOperationRecord()['手术部位'] || getOperationRecord()['operation_site'] || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="术前主要诊断">
            {{ getOperationRecord()['术前主要诊断名称'] || getOperationRecord()['pre_operation_diagnosis'] || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="术中主要诊断">
            {{ getOperationRecord()['术中主要诊断名称'] || getOperationRecord()['intra_operation_diagnosis'] || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="术后主要诊断" :span="2">
            {{ getOperationRecord()['术后主要诊断名称'] || getOperationRecord()['post_operation_diagnosis'] || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="术中出血">
            {{ getOperationRecord()['术中出血'] || getOperationRecord()['intra_operation_bleeding'] || '-' }}
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <div class="section" v-if="getOperationRecord() && (getOperationRecord()['手术经过'] || getOperationRecord()['operation_process'])">
        <div class="section-title">手术经过</div>
        <div class="text-content">
          {{ formatCourseContent(getOperationRecord()['手术经过'] || getOperationRecord()['operation_process'] || '') }}
        </div>
      </div>

      <div class="section" v-if="getOperationRecord() && (getOperationRecord()['术中发现'] || getOperationRecord()['intra_operation_findings'])">
        <div class="section-title">术中发现</div>
        <div class="text-content">
          {{ formatCourseContent(getOperationRecord()['术中发现'] || getOperationRecord()['intra_operation_findings'] || '') }}
        </div>
      </div>

      <div class="section" v-if="getOperationRecord() && (getOperationRecord()['术中处理'] || getOperationRecord()['intra_operation_treatment'])">
        <div class="section-title">术中处理</div>
        <div class="text-content">
          {{ formatCourseContent(getOperationRecord()['术中处理'] || getOperationRecord()['intra_operation_treatment'] || '') }}
        </div>
      </div>
      <el-empty v-else description="暂无手术记录" />
    </div>

    <!-- 病程记录页面 -->
    <div class="record-page" v-if="currentPage === 'course'">
      <div class="page-header">
        <h2>病程记录</h2>
        <div class="page-number">共 {{ getCourseRecords().length }} 条记录</div>
      </div>

      <div v-if="getCourseRecords().length > 0" class="course-records">
        <el-timeline>
          <el-timeline-item
            v-for="(record, index) in getCourseRecords()"
            :key="index"
            :timestamp="formatRecordTime(record.记录时间 || record.record_time)"
            placement="top"
            size="large"
          >
            <el-card shadow="hover" class="course-card">
              <div class="course-header">
                <el-tag size="small" type="info">{{ record.类型 || record.type || '病程记录类' }}</el-tag>
                <span class="course-id" v-if="record.流水号 || record.serial_number">
                  流水号: {{ record.流水号 || record.serial_number }}
                </span>
              </div>
              <div class="course-content">
                {{ formatCourseContent(record.文档内容 || record.content || record.document_content) }}
              </div>
            </el-card>
          </el-timeline-item>
        </el-timeline>
      </div>
      <el-empty v-else description="暂无病程记录" />
    </div>

    <!-- 医嘱页面 -->
    <div class="record-page" v-if="currentPage === 'orders'">
      <div class="page-header">
        <h2>医嘱记录</h2>
        <div class="page-number">共 {{ getOrders().length }} 条医嘱</div>
      </div>

      <div v-if="getOrders().length > 0" class="orders-section">
        <!-- 筛选和搜索 -->
        <div class="orders-toolbar">
          <el-input
            v-model="orderSearchKeyword"
            placeholder="搜索医嘱项目名称"
            clearable
            style="width: 300px"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-select
            v-model="orderTypeFilter"
            placeholder="筛选医嘱类型"
            clearable
            style="width: 200px; margin-left: 12px;"
          >
            <el-option label="全部" value="" />
            <el-option label="住院长期医嘱" value="住院长期医嘱" />
            <el-option label="住院临时医嘱" value="住院临时医嘱" />
          </el-select>
          <el-select
            v-model="orderStatusFilter"
            placeholder="筛选状态"
            clearable
            style="width: 150px; margin-left: 12px;"
          >
            <el-option label="全部" value="" />
            <el-option label="执行中" value="执行中" />
            <el-option label="停嘱" value="停嘱" />
            <el-option label="复核通过" value="复核通过" />
          </el-select>
        </div>

        <!-- 医嘱表格 -->
        <el-table
          :data="filteredOrders"
          border
          stripe
          style="margin-top: 16px;"
          max-height="600"
        >
          <el-table-column type="index" label="#" width="60" align="center" />
          <el-table-column prop="医嘱类型名称" label="医嘱类型" width="140" align="center">
            <template #default="{ row }">
              {{ row.医嘱类型名称 || row.order_type_name || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="医嘱项目名称" label="医嘱项目" min-width="200" show-overflow-tooltip>
            <template #default="{ row }">
              {{ row.医嘱项目名称 || row.order_item_name || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="单次剂量" label="单次剂量" width="100" align="center">
            <template #default="{ row }">
              {{ row.单次剂量 || row.single_dose || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="使用频率" label="使用频率" width="120" align="center">
            <template #default="{ row }">
              {{ row.使用频率 || row.frequency || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="医嘱下达时间" label="下达时间" width="120" align="center">
            <template #default="{ row }">
              {{ row.医嘱下达时间 || row.order_time || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="医嘱开始时间" label="开始时间" width="120" align="center">
            <template #default="{ row }">
              {{ row.医嘱开始时间 || row.start_time || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="医嘱停止时间" label="停止时间" width="120" align="center">
            <template #default="{ row }">
              {{ row.医嘱停止时间 || row.stop_time || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="状态" label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag
                :type="getOrderStatusType(row.状态 || row.status)"
                size="small"
              >
                {{ row.状态 || row.status || '-' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="医嘱备注" label="备注" min-width="150" show-overflow-tooltip>
            <template #default="{ row }">
              {{ row.医嘱备注 || row.remark || '-' }}
            </template>
          </el-table-column>
        </el-table>
      </div>
      <el-empty v-else description="暂无医嘱记录" />
    </div>

    <!-- 其他页面 -->
    <div class="record-page" v-else>
      <div class="page-header">
        <h2>{{ getPageTitle() }}</h2>
      </div>
      <el-empty description="暂无内容" />
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { PropType } from 'vue'
import { Search } from '@element-plus/icons-vue'

const props = defineProps({
  data: {
    type: Object as PropType<Record<string, any>>,
    required: true
  }
})

const currentPage = ref<'basic' | 'diagnosis' | 'surgery' | 'admission' | 'discharge' | 'operation' | 'course' | 'orders'>('basic')
const orderSearchKeyword = ref('')
const orderTypeFilter = ref('')
const orderStatusFilter = ref('')

// 获取字段值（支持多种可能的路径）
const getFieldValue = (...pathArrays: string[][]): string => {
  // 尝试所有传入的路径
  for (const path of pathArrays) {
    let current: any = props.data
    
    for (const key of path) {
      if (current && typeof current === 'object') {
        // 尝试精确匹配
        if (key in current) {
          current = current[key]
        } else {
          // 尝试模糊匹配（忽略大小写、空格等）
          const foundKey = Object.keys(current).find(k => 
            k.toLowerCase().replace(/\s+/g, '') === key.toLowerCase().replace(/\s+/g, '')
          )
          if (foundKey) {
            current = current[foundKey]
          } else {
            current = null
            break
          }
        }
      } else {
        current = null
        break
      }
    }
    
    if (current !== null && current !== undefined) {
      // 如果是数组，转换为字符串
      if (Array.isArray(current)) {
        return current.map(item => 
          typeof item === 'object' ? (item.name || item.value || JSON.stringify(item)) : String(item)
        ).join('、')
      }
      
      // 如果是对象，尝试提取常用字段
      if (typeof current === 'object') {
        // 如果是简单对象，尝试提取name、value等字段
        if (current.name) return String(current.name)
        if (current.value) return String(current.value)
        if (current.text) return String(current.text)
        // 否则返回JSON字符串
        return JSON.stringify(current, null, 2)
      }
      
      return String(current)
    }
  }
  
  return ''
}

// 获取其他诊断
const getOtherDiagnoses = (): string[] => {
  const diagnoses: string[] = []
  
  // 尝试多种可能的字段路径
  const value = getFieldValue(
    ['诊断信息', '其他诊断'],
    ['诊断', '其他诊断'],
    ['诊断信息', '次要诊断'],
    ['诊断', '次要诊断']
  )
  
  if (value) {
    // 如果是字符串，尝试分割
    const items = value.split(/[、,，;；]/).filter(item => item.trim())
    diagnoses.push(...items)
  }
  
  // 如果诊断信息是数组
  if (props.data['诊断信息'] && Array.isArray(props.data['诊断信息'])) {
    return props.data['诊断信息'].map((d: any) => 
      typeof d === 'string' ? d : (d.name || d.diagnosis || String(d))
    )
  }
  
  return diagnoses
}

// 检查是否有手术信息
const hasSurgeryInfo = (): boolean => {
  return !!(
    getFieldValue(['手术信息', '手术名称'], ['手术', '手术名称'], ['手术名称']) ||
    props.data['手术信息'] ||
    props.data['手术']
  )
}

// 获取其他信息（不在标准字段中的信息）
const getOtherInfo = (): Record<string, string> => {
  const otherInfo: Record<string, string> = {}
  const standardFields = [
    '患者信息', '基本信息', '诊断信息', '诊断', '手术信息', '手术',
    '主诉', '现病史', '既往史', '个人史', '家族史'
  ]
  
  for (const [key, value] of Object.entries(props.data)) {
    if (!standardFields.includes(key) && typeof value !== 'object') {
      otherInfo[key] = String(value)
    } else if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
      // 检查是否是嵌套对象，但不在标准字段中
      if (!standardFields.includes(key)) {
        // 尝试提取一些常见字段
        for (const [subKey, subValue] of Object.entries(value)) {
          if (typeof subValue !== 'object' || subValue === null) {
            otherInfo[`${key}.${subKey}`] = String(subValue)
          }
        }
      }
    }
  }
  
  return otherInfo
}

// 检查是否有其他信息
const hasOtherInfo = (): boolean => {
  return Object.keys(getOtherInfo()).length > 0
}

// 获取病程记录
const getCourseRecords = (): any[] => {
  const records = props.data['病程记录'] || props.data['course_records'] || props.data['courseRecords'] || []
  if (Array.isArray(records)) {
    return records
  }
  return []
}

// 格式化病程记录时间
const formatRecordTime = (time: string): string => {
  if (!time) return ''
  // 处理各种时间格式
  return time.replace(/\//g, '-')
}

// 格式化病程记录内容（处理转义字符）
const formatCourseContent = (content: string): string => {
  if (!content) return ''
  // 处理 \n 转义字符
  return content.replace(/\\n/g, '\n').replace(/\\t/g, '\t')
}

// 获取医嘱记录
const getOrders = (): any[] => {
  const orders = props.data['医嘱'] || props.data['orders'] || props.data['medical_orders'] || []
  if (Array.isArray(orders)) {
    return orders
  }
  return []
}

// 过滤后的医嘱
const filteredOrders = computed(() => {
  let orders = getOrders()
  
  // 搜索过滤
  if (orderSearchKeyword.value) {
    const keyword = orderSearchKeyword.value.trim().toLowerCase()
    orders = orders.filter(order => {
      const itemName = (order.医嘱项目名称 || order.order_item_name || '').toLowerCase()
      return itemName.includes(keyword)
    })
  }
  
  // 类型过滤
  if (orderTypeFilter.value) {
    orders = orders.filter(order => {
      const type = order.医嘱类型名称 || order.order_type_name || ''
      return type === orderTypeFilter.value
    })
  }
  
  // 状态过滤
  if (orderStatusFilter.value) {
    orders = orders.filter(order => {
      const status = order.状态 || order.status || ''
      return status === orderStatusFilter.value
    })
  }
  
  return orders
})

// 获取医嘱状态标签类型
const getOrderStatusType = (status: string): '' | 'success' | 'warning' | 'danger' | 'info' => {
  if (!status) return ''
  if (status.includes('执行') || status.includes('进行')) return 'success'
  if (status.includes('停') || status.includes('取消')) return 'warning'
  if (status.includes('复核') || status.includes('通过')) return 'info'
  return ''
}

// 获取病案首页数据
const getHomePageData = (): any => {
  return props.data['病案首页'] || props.data['home_page'] || props.data['homePage'] || {}
}

// 获取其他诊断列表
const getOtherDiagnosesList = (): any[] => {
  const diagnoses = props.data['病案首页-出院其他诊断'] || 
                    props.data['home_page_other_diagnoses'] || 
                    props.data['other_diagnoses'] || []
  if (Array.isArray(diagnoses)) {
    return diagnoses
  }
  return []
}

// 格式化入院病情
const formatAdmissionCondition = (condition: any): string => {
  if (!condition) return '-'
  const conditionMap: Record<string, string> = {
    '1.0': '有',
    '1': '有',
    '2.0': '临床未确定',
    '2': '临床未确定',
    '3.0': '情况不明',
    '3': '情况不明',
    '4.0': '无',
    '4': '无'
  }
  return conditionMap[String(condition)] || String(condition)
}

// 获取其他手术操作
const getOtherSurgeries = (): any[] => {
  const surgeries = props.data['病案首页-其他手术操作'] || 
                    props.data['home_page_other_surgeries'] || 
                    props.data['other_surgeries'] || []
  if (Array.isArray(surgeries)) {
    return surgeries
  }
  return []
}

// 获取入院记录
const getAdmissionRecord = (): any => {
  return props.data['入院记录'] || props.data['admission_record'] || props.data['admissionRecord'] || {}
}

// 获取出院记录
const getDischargeRecord = (): any => {
  return props.data['出院记录'] || props.data['discharge_record'] || props.data['dischargeRecord'] || {}
}

// 获取手术记录
const getOperationRecord = (): any => {
  return props.data['手术记录'] || props.data['operation_record'] || props.data['operationRecord'] || {}
}

// 处理标签切换
const handleTabChange = (name: string) => {
  currentPage.value = name as any
}

// 获取页面标题
const getPageTitle = (): string => {
  const titles: Record<string, string> = {
    basic: '基本信息',
    diagnosis: '诊断信息',
    surgery: '手术信息',
    admission: '入院记录',
    discharge: '出院记录',
    operation: '手术记录',
    course: '病程记录',
    orders: '医嘱记录'
  }
  return titles[currentPage.value] || '未知页面'
}
</script>

<style scoped>
.medical-record-view {
  background: #ffffff;
  min-height: 600px;
}

.record-page {
  padding: 24px;
  background: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  margin-bottom: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid #409eff;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.page-number {
  font-size: 14px;
  color: #909399;
}

.section {
  margin-bottom: 24px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
  padding-left: 8px;
  border-left: 4px solid #409eff;
}

.text-content {
  padding: 16px;
  background: #f5f7fa;
  border-radius: 4px;
  line-height: 1.8;
  color: #606266;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.page-navigation-top {
  margin-bottom: 20px;
  background: #ffffff;
  position: sticky;
  top: 0;
  z-index: 10;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.page-navigation-top :deep(.el-tabs__header) {
  margin: 0;
  padding: 0 16px;
}

.page-navigation-top :deep(.el-tabs__nav-wrap) {
  padding: 0;
}

.page-navigation-top :deep(.el-tabs__item) {
  padding: 0 20px;
  height: 40px;
  line-height: 40px;
}

/* 病程记录样式 */
.course-records {
  margin-top: 20px;
}

.course-card {
  margin-bottom: 16px;
}

.course-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.course-id {
  font-size: 12px;
  color: #909399;
}

.course-content {
  white-space: pre-wrap;
  word-wrap: break-word;
  line-height: 1.8;
  color: #606266;
  font-size: 14px;
  max-height: 500px;
  overflow-y: auto;
  padding: 12px;
  background: #fafafa;
  border-radius: 4px;
}

/* 医嘱样式 */
.orders-section {
  margin-top: 20px;
}

.orders-toolbar {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

/* 打印样式 */
@media print {
  .page-navigation-top {
    display: none;
  }
  
  .record-page {
    page-break-after: always;
    border: none;
    padding: 0;
  }
  
  .orders-toolbar {
    display: none;
  }
}
</style>

