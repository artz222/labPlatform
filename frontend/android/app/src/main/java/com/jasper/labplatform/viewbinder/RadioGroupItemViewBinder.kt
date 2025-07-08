package com.jasper.labplatform.viewbinder

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.RadioButton
import android.widget.RadioGroup
import androidx.core.view.isNotEmpty
import androidx.recyclerview.widget.RecyclerView
import com.drakeet.multitype.ItemViewBinder
import com.google.android.material.snackbar.Snackbar
import com.jasper.labplatform.R
import com.jasper.labplatform.repository.model.Options

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
                    id = index + 1
                })
            }
            submitBtn.apply {
                setOnClickListener {
                    Snackbar.make(
                        holder.itemView,
                        radioGroup.checkedRadioButtonId.toString(),
                        Snackbar.LENGTH_SHORT
                    ).show()
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
}