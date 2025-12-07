import { format } from 'date-fns-jalali';

export function formatDate(date: string | Date | undefined | null, formatStr: string = 'yyyy/MM/dd HH:mm'): string {
    if (!date) return '';
    const d = typeof date === 'string' ? new Date(date) : date;
    return format(d, formatStr);
}
