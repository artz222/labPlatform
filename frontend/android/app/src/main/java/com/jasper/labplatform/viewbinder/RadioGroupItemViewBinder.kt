package com.jasper.labplatform.viewbinder

import android.content.Context
import android.view.Gravity
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.view.ViewGroup.LayoutParams.MATCH_PARENT
import android.view.ViewGroup.LayoutParams.WRAP_CONTENT
import android.widget.Button
import android.widget.RadioButton
import android.widget.RadioGroup
import android.widget.TextView
import androidx.core.view.isNotEmpty
import androidx.recyclerview.widget.RecyclerView
import com.drakeet.multitype.ItemViewBinder
import com.google.android.material.dialog.MaterialAlertDialogBuilder
import com.google.android.material.snackbar.Snackbar
import com.jasper.labplatform.R
import com.jasper.labplatform.repository.Repository
import com.jasper.labplatform.repository.model.Options
import com.jasper.labplatform.utils.ext.dpToPx

class RadioGroupItemViewBinder : ItemViewBinder<Options, RadioGroupItemViewBinder.ViewHolder>() {
    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val radioGroup: RadioGroup = itemView.findViewById(R.id.radioGroup)
        val submitBtn: Button = itemView.findViewById(R.id.submitBtn)
    }

    override fun onBindViewHolder(holder: ViewHolder, item: Options) {
        holder.apply {
            if (radioGroup.isNotEmpty()) return
            item.options.forEachIndexed { index, option ->
                radioGroup.addView(RadioButton(itemView.context).apply {
                    text = option
                    id = index
                })
            }
            submitBtn.apply {
                setOnClickListener {
                    if (radioGroup.checkedRadioButtonId < 0) {
                        Snackbar.make(
                            holder.itemView,
                            "请选择后再提交～",
                            Snackbar.LENGTH_SHORT
                        ).show()
                    } else
                        showDecisionDialog(context, item.options[radioGroup.checkedRadioButtonId])
                }
            }
        }
    }

    override fun onCreateViewHolder(
        inflater: LayoutInflater,
        parent: ViewGroup
    ): ViewHolder {
        return ViewHolder(inflater.inflate(R.layout.item_radio_group, parent, false))
    }

    private fun showDecisionDialog(context: Context, curOption: String) {
        MaterialAlertDialogBuilder(context)
            .setTitle("请确认你的选择")
            .setView(TextView(context).apply {
                text = curOption
                textSize = 18f
                layoutParams = ViewGroup.LayoutParams(MATCH_PARENT, WRAP_CONTENT)
                setPadding(34.dpToPx(), 0, 0, 0)
                gravity = Gravity.CENTER_VERTICAL
                minHeight = 48.dpToPx()
            }) // Set the custom view
            .setPositiveButton("确认") { dialog, which ->
                Repository.submitDecision(curOption)
            }
            .setNegativeButton("取消") { dialog, which ->
                dialog.dismiss()
            }
            .setCancelable(true) // Optional: Prevent dismissing by tapping outside or back press
            .show()
    }
}