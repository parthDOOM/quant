import React from 'react';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import '../styles/datepicker.css';

interface DatePickerWrapperProps {
  value: string;
  onChange: (date: string) => void;
  min?: string;
  max?: string;
  disabled?: boolean;
  className?: string;
}

export default function DatePickerWrapper({ value, onChange, min, max, disabled, className }: DatePickerWrapperProps) {
  return (
    <DatePicker
      selected={value ? new Date(value) : null}
      onChange={date => date && onChange(date.toISOString().slice(0, 10))}
      minDate={min ? new Date(min) : undefined}
      maxDate={max ? new Date(max) : undefined}
      dateFormat="yyyy-MM-dd"
      className={className}
      disabled={disabled}
      showPopperArrow={false}
      popperPlacement="bottom"
      calendarClassName="react-datepicker"
      wrapperClassName="w-full"
    />
  );
}
